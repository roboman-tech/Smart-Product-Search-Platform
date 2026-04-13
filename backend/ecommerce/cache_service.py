"""Redis-backed JSON caching for API payloads.

Uses Django's ``cache`` backend (django-redis in production, LocMem when disabled).
All JSON values are serialized with ``default=str`` so Decimals and ORM types round-trip safely.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheJSON:
    """Thin wrapper around Django cache for JSON-serializable API payloads."""

    @staticmethod
    def get(key: str) -> Any | None:
        raw = cache.get(key)
        if raw is None:
            return None
        if not isinstance(raw, str):
            logger.warning("cache value for %s is not a string; ignoring", key)
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("cache corrupt JSON for key %s", key)
            return None

    @staticmethod
    def set(key: str, value: Any, timeout_seconds: int) -> None:
        payload = json.dumps(value, default=str)
        cache.set(key, payload, timeout_seconds)

    @staticmethod
    def delete(key: str) -> None:
        cache.delete(key)


def search_cache_key(
    normalized_query: str,
    category: str,
    brand: str,
    min_price: str,
    max_price: str,
    rating: str,
    in_stock: str,
    sort: str,
    page: int,
    page_size: int,
) -> str:
    """Stable key for paginated search; query segment is hashed to avoid unsafe characters."""
    qh = hashlib.sha256(normalized_query.encode("utf-8")).hexdigest()[:24]
    return (
        f"search:{qh}:{category}:{brand}:{min_price}:"
        f"{max_price}:{rating}:{in_stock}:{sort}:{page}:{page_size}"
    )


def product_detail_key(product_id: int) -> str:
    return f"product:{product_id}"


def categories_key() -> str:
    return "categories:all"


def brands_key() -> str:
    return "brands:all"


def related_key(product_id: int) -> str:
    return f"related:{product_id}"


def recommendations_key(product_id: int) -> str:
    return f"recommendations:{product_id}"


def get_cache_ttl_seconds(name: str) -> int:
    """Resolve TTL from ``settings.CACHE_TTLS`` with sensible default."""
    return int(getattr(settings, "CACHE_TTLS", {}).get(name, 600))


def invalidate_product_caches(product_id: int) -> None:
    """Invalidate caches tied to a single product (detail, related, recommendations)."""
    CacheJSON.delete(product_detail_key(product_id))
    CacheJSON.delete(related_key(product_id))
    CacheJSON.delete(recommendations_key(product_id))


def invalidate_category_list_cache() -> None:
    CacheJSON.delete(categories_key())


def invalidate_brand_list_cache() -> None:
    CacheJSON.delete(brands_key())
