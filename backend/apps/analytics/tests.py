"""Analytics service tests."""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.analytics.models import SearchLog
from apps.products.models import Brand, Category, Product


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
def test_create_search_log_record_via_endpoint(api):
    url = reverse("search-log")
    r = api.post(
        url,
        {"query": "shoes", "result_count": 5},
        format="json",
    )
    assert r.status_code == 201
    assert SearchLog.objects.filter(query="shoes", result_count=5).exists()


@pytest.mark.django_db
def test_recommendation_click_service_creates_row(api):
    cat = Category.objects.create(name="C", slug="c")
    brand = Brand.objects.create(name="B", slug="b")
    s = Product.objects.create(
        name="S",
        slug="s",
        short_description="",
        description="",
        category=cat,
        brand=brand,
        price="1.00",
        rating="4.0",
        review_count=1,
        stock_quantity=1,
        is_active=True,
        popularity_score=1,
    )
    t = Product.objects.create(
        name="T",
        slug="t",
        short_description="",
        description="",
        category=cat,
        brand=brand,
        price="2.00",
        rating="4.0",
        review_count=1,
        stock_quantity=1,
        is_active=True,
        popularity_score=1,
    )
    r = api.post(
        reverse("recommendation-click"),
        {"source_product": s.pk, "recommended_product": t.pk},
        format="json",
    )
    assert r.status_code == 201
