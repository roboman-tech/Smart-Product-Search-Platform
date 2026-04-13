from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Mapping

from django.db.models import Prefetch, Q, QuerySet
from rest_framework.exceptions import ValidationError

from apps.products.models import Product, ProductAttribute, ProductImage, ProductTag

VALID_SORTS = frozenset(
    {
        "relevance",
        "price_asc",
        "price_desc",
        "newest",
        "rating_desc",
        "popularity_desc",
    }
)


def parse_bool_param(value: str | None) -> bool | None:
    if value is None or value == "":
        return None
    v = value.lower()
    if v in ("1", "true", "yes"):
        return True
    if v in ("0", "false", "no"):
        return False
    raise ValidationError({"in_stock": "Must be a boolean."})


def parse_decimal(value: str | None, field: str) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        raise ValidationError({field: "Invalid number."})


def parse_rating(value: str | None) -> Decimal | None:
    if value is None or value == "":
        return None
    d = parse_decimal(value, "rating")
    if d is not None and (d < 0 or d > 5):
        raise ValidationError({"rating": "Rating must be between 0 and 5."})
    return d


def resolve_category_filter(category_param: str | None) -> Q:
    if not category_param:
        return Q()
    if category_param.isdigit():
        return Q(category_id=int(category_param))
    return Q(category__slug=category_param)


def resolve_brand_filter(brand_param: str | None) -> Q:
    if not brand_param:
        return Q()
    if brand_param.isdigit():
        return Q(brand_id=int(brand_param))
    return Q(brand__slug=brand_param)


def apply_product_filters(
    qs: QuerySet[Product],
    *,
    category: str | None,
    brand: str | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    rating: Decimal | None,
    in_stock: bool | None,
) -> QuerySet[Product]:
    qs = qs.filter(is_active=True)
    qs = qs.filter(resolve_category_filter(category))
    qs = qs.filter(resolve_brand_filter(brand))
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    if rating is not None:
        qs = qs.filter(rating__gte=rating)
    if in_stock is True:
        qs = qs.filter(stock_quantity__gt=0)
    elif in_stock is False:
        qs = qs.filter(stock_quantity=0)
    return qs


def validate_price_range(min_price: Decimal | None, max_price: Decimal | None) -> None:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise ValidationError({"min_price": "min_price cannot exceed max_price."})


def validate_sort(sort: str) -> None:
    if sort not in VALID_SORTS:
        raise ValidationError(
            {"sort": f"Invalid sort. Allowed: {', '.join(sorted(VALID_SORTS))}."}
        )


def apply_sort(qs: QuerySet[Product], sort: str, has_relevance: bool) -> QuerySet[Product]:
    if sort == "relevance":
        if has_relevance:
            return qs.order_by("-search_score", "-rating", "-popularity_score", "id")
        return qs.order_by("-popularity_score", "-rating", "id")
    if sort == "price_asc":
        return qs.order_by("price", "id")
    if sort == "price_desc":
        return qs.order_by("-price", "id")
    if sort == "newest":
        return qs.order_by("-created_at", "id")
    if sort == "rating_desc":
        return qs.order_by("-rating", "-review_count", "id")
    if sort == "popularity_desc":
        return qs.order_by("-popularity_score", "-rating", "id")
    return qs


def default_sort_for_request(q: str | None, explicit_sort: str | None) -> str:
    if explicit_sort:
        return explicit_sort
    if q and q.strip():
        return "relevance"
    return "popularity_desc"


def product_list_base_queryset() -> QuerySet[Product]:
    return (
        Product.objects.filter(is_active=True)
        .select_related("category", "brand")
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.order_by("-is_primary", "id"),
            ),
            Prefetch("tags", queryset=ProductTag.objects.order_by("tag")),
        )
    )


def product_detail_base_queryset() -> QuerySet[Product]:
    return (
        Product.objects.filter(is_active=True)
        .select_related("category", "brand")
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.order_by("-is_primary", "id"),
            ),
            Prefetch("tags", queryset=ProductTag.objects.order_by("tag")),
            Prefetch(
                "attributes",
                queryset=ProductAttribute.objects.order_by("attribute_name"),
            ),
        )
    )


def build_product_list_queryset(
    query_params: Mapping[str, str | None],
) -> QuerySet[Product]:
    """Apply filters and sort for ``GET /api/products/`` (no relevance scoring)."""
    p = query_params
    min_p = parse_decimal(p.get("min_price"), "min_price")
    max_p = parse_decimal(p.get("max_price"), "max_price")
    validate_price_range(min_p, max_p)
    rating = parse_rating(p.get("rating"))
    in_stock = parse_bool_param(p.get("in_stock"))
    sort_raw = p.get("sort")
    if sort_raw:
        validate_sort(sort_raw)
        sort = sort_raw
    else:
        sort = default_sort_for_request(None, None)
    validate_sort(sort)

    qs = product_list_base_queryset()
    qs = apply_product_filters(
        qs,
        category=p.get("category"),
        brand=p.get("brand"),
        min_price=min_p,
        max_price=max_p,
        rating=rating,
        in_stock=in_stock,
    )
    return apply_sort(qs, sort, has_relevance=False)
