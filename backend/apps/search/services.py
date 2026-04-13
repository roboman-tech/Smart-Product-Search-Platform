"""Search scoring, filtering, sorting, pagination, and Redis-backed response caching."""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Case, Exists, F, IntegerField, OuterRef, Q, QuerySet, Value, When
from django.db.models.functions import Cast
from django.http import QueryDict

from apps.products.models import Product, ProductTag
from apps.products.serializers import ProductListSerializer
from apps.products.services import (
    apply_product_filters,
    apply_sort,
    default_sort_for_request,
    parse_bool_param,
    parse_decimal,
    parse_rating,
    product_list_base_queryset,
    validate_price_range,
    validate_sort,
)
from ecommerce.cache_service import CacheJSON, get_cache_ttl_seconds, search_cache_key
from ecommerce.pagination import parse_page_params


def normalize_query(q: str | None) -> str:
    return (q or "").strip().lower()


def annotate_search_score(qs: QuerySet[Product], q_norm: str) -> QuerySet[Product]:
    if not q_norm:
        return qs.annotate(search_score=Value(0, output_field=IntegerField()))

    tag_exists = Exists(
        ProductTag.objects.filter(product_id=OuterRef("pk")).filter(
            Q(tag__iexact=q_norm) | Q(tag__icontains=q_norm)
        )
    )

    tier = Case(
        When(name__iexact=q_norm, then=Value(1_000_000)),
        When(name__icontains=q_norm, then=Value(500_000)),
        default=Value(0),
        output_field=IntegerField(),
    )
    tag_bonus = Case(
        When(tag_exists, then=Value(300_000)),
        default=Value(0),
        output_field=IntegerField(),
    )
    brand_bonus = Case(
        When(brand__name__icontains=q_norm, then=Value(200_000)),
        default=Value(0),
        output_field=IntegerField(),
    )
    cat_bonus = Case(
        When(category__name__icontains=q_norm, then=Value(150_000)),
        default=Value(0),
        output_field=IntegerField(),
    )
    desc_bonus = Case(
        When(
            Q(description__icontains=q_norm) | Q(short_description__icontains=q_norm),
            then=Value(100_000),
        ),
        default=Value(0),
        output_field=IntegerField(),
    )
    stock_boost = Case(
        When(stock_quantity__gt=0, then=Value(5_000)),
        default=Value(0),
        output_field=IntegerField(),
    )
    rating_int = Cast(F("rating") * 100, IntegerField())

    return qs.annotate(
        search_score=(
            tier
            + tag_bonus
            + brand_bonus
            + cat_bonus
            + desc_bonus
            + stock_boost
            + F("popularity_score")
            + rating_int
        )
    ).distinct()


def run_search(
    *,
    q: str | None,
    category: str | None,
    brand: str | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    rating: Decimal | None,
    in_stock: bool | None,
    sort_param: str | None,
) -> tuple[QuerySet[Product], str, bool]:
    validate_price_range(min_price, max_price)
    q_norm = normalize_query(q)
    sort = default_sort_for_request(q, sort_param)
    validate_sort(sort)

    qs = product_list_base_queryset()
    qs = apply_product_filters(
        qs,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        rating=rating,
        in_stock=in_stock,
    )
    has_relevance = bool(q_norm)
    if has_relevance:
        qs = annotate_search_score(qs, q_norm)
        qs = qs.filter(search_score__gt=0)
    else:
        qs = qs.annotate(search_score=Value(0, output_field=IntegerField()))

    qs = apply_sort(qs, sort, has_relevance=has_relevance)
    return qs, sort, has_relevance


def search_response_dict(
    *,
    query: str,
    total: int,
    page: int,
    page_size: int,
    sort: str,
    results: list,
) -> dict:
    return {
        "query": query,
        "total": total,
        "page": page,
        "page_size": page_size,
        "sort": sort,
        "results": results,
    }


def search_products(query_params: QueryDict) -> dict:
    """Execute search with filters, sort, pagination, cache, and serialization."""
    page, page_size = parse_page_params(query_params)
    min_p = parse_decimal(query_params.get("min_price"), "min_price")
    max_p = parse_decimal(query_params.get("max_price"), "max_price")
    rating = parse_rating(query_params.get("rating"))
    in_stock_raw = query_params.get("in_stock")
    in_stock = (
        parse_bool_param(in_stock_raw)
        if in_stock_raw not in (None, "")
        else None
    )
    category = query_params.get("category") or ""
    brand = query_params.get("brand") or ""
    q_raw = query_params.get("q") or ""
    sort_param = query_params.get("sort") or None

    validate_price_range(min_p, max_p)
    q_norm = normalize_query(q_raw)
    sort_resolved = default_sort_for_request(q_raw, sort_param)
    validate_sort(sort_resolved)

    in_stock_key = ""
    if in_stock is not None:
        in_stock_key = "1" if in_stock else "0"

    cache_key = search_cache_key(
        q_norm,
        category,
        brand,
        str(min_p) if min_p is not None else "",
        str(max_p) if max_p is not None else "",
        str(rating) if rating is not None else "",
        in_stock_key,
        sort_resolved,
        page,
        page_size,
    )
    cached = CacheJSON.get(cache_key)
    if cached is not None:
        return cached

    qs, sort, _ = run_search(
        q=q_raw,
        category=category or None,
        brand=brand or None,
        min_price=min_p,
        max_price=max_p,
        rating=rating,
        in_stock=in_stock,
        sort_param=sort_param,
    )
    total = qs.count()
    start = (page - 1) * page_size
    page_qs = qs[start : start + page_size]
    results = ProductListSerializer(page_qs, many=True).data
    body = search_response_dict(
        query=q_raw.strip(),
        total=total,
        page=page,
        page_size=page_size,
        sort=sort,
        results=list(results),
    )
    CacheJSON.set(cache_key, body, get_cache_ttl_seconds("search"))
    return body
