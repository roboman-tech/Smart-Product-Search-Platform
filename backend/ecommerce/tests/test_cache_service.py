"""Tests for JSON cache helpers (LocMem in test settings)."""

from __future__ import annotations

from ecommerce.cache_service import CacheJSON, search_cache_key


def test_cache_json_roundtrip():
    key = "test:cache-json-roundtrip"
    CacheJSON.delete(key)
    CacheJSON.set(key, {"a": 1, "b": [2, 3]}, 60)
    assert CacheJSON.get(key) == {"a": 1, "b": [2, 3]}
    CacheJSON.delete(key)
    assert CacheJSON.get(key) is None


def test_search_cache_key_stable_for_same_inputs():
    k1 = search_cache_key("laptop", "1", "", "", "", "", "", "relevance", 1, 20)
    k2 = search_cache_key("laptop", "1", "", "", "", "", "", "relevance", 1, 20)
    assert k1 == k2
