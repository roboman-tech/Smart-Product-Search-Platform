"""Catalog read models: list/detail/related/recommendations with Redis caching."""

from __future__ import annotations

from django.db.models import Prefetch
from django.http import Http404

from apps.products.models import Brand, Category, Product, ProductImage, ProductTag
from apps.products.serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductDetailSerializer,
)
from apps.products.services import product_detail_base_queryset
from apps.recommendations.services import get_related_products, get_recommendations
from ecommerce.cache_service import (
    CacheJSON,
    brands_key,
    categories_key,
    get_cache_ttl_seconds,
    product_detail_key,
    recommendations_key,
    related_key,
)


def list_categories_payload() -> list[dict]:
    """Return all categories; cached under ``categories:all``."""
    key = categories_key()
    cached = CacheJSON.get(key)
    if cached is not None:
        return cached
    data = CategorySerializer(
        Category.objects.all().order_by("name"),
        many=True,
    ).data
    data_list = list(data)
    CacheJSON.set(key, data_list, get_cache_ttl_seconds("categories"))
    return data_list


def list_brands_payload() -> list[dict]:
    """Return all brands; cached under ``brands:all``."""
    key = brands_key()
    cached = CacheJSON.get(key)
    if cached is not None:
        return cached
    data = BrandSerializer(Brand.objects.all().order_by("name"), many=True).data
    data_list = list(data)
    CacheJSON.set(key, data_list, get_cache_ttl_seconds("brands"))
    return data_list


def get_product_detail_payload(product_id: int) -> dict:
    """Full product detail JSON; cached per ``product:{id}``."""
    key = product_detail_key(product_id)
    cached = CacheJSON.get(key)
    if cached is not None:
        return cached
    qs = product_detail_base_queryset()
    try:
        product = qs.get(pk=product_id)
    except Product.DoesNotExist:
        raise Http404()
    payload = dict(ProductDetailSerializer(product).data)
    CacheJSON.set(key, payload, get_cache_ttl_seconds("product_detail"))
    return payload


def _product_with_media(product_id: int) -> Product:
    try:
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
            .get(pk=product_id)
        )
    except Product.DoesNotExist:
        raise Http404()


def get_related_products_payload(product_id: int) -> list[dict]:
    """Rule-based related products; cached under ``related:{id}``."""
    key = related_key(product_id)
    cached = CacheJSON.get(key)
    if cached is not None:
        return cached
    product = _product_with_media(product_id)
    payload = get_related_products(product, limit=10)
    CacheJSON.set(key, payload, get_cache_ttl_seconds("related"))
    return payload


def get_recommendations_payload(product_id: int) -> list[dict]:
    """Rule-based recommendations; cached under ``recommendations:{id}``."""
    key = recommendations_key(product_id)
    cached = CacheJSON.get(key)
    if cached is not None:
        return cached
    product = _product_with_media(product_id)
    payload = get_recommendations(product, limit=12)
    CacheJSON.set(key, payload, get_cache_ttl_seconds("recommendations"))
    return payload
