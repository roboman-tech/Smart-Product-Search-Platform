import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.products.models import Brand, Category, Product


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
def test_search_keyword_and_cache(api):
    cat = Category.objects.create(name="Audio", slug="audio")
    brand = Brand.objects.create(name="SoundMax", slug="soundmax")
    Product.objects.create(
        name="Wireless Headphones X1",
        slug="wh-x1",
        short_description="Great sound",
        description="Bluetooth wireless headphones with long battery life.",
        category=cat,
        brand=brand,
        price="149.99",
        rating="4.6",
        review_count=10,
        stock_quantity=5,
        is_active=True,
        popularity_score=100,
    )

    url = reverse("search")
    r = api.get(url, {"q": "wireless headphones"})
    assert r.status_code == 200
    assert r.data["total"] >= 1
    assert r.data["sort"] == "relevance"

    r2 = api.get(url, {"q": "wireless headphones"})
    assert r2.status_code == 200

    r3 = api.get(url, {"sort": "bad"})
    assert r3.status_code == 400


@pytest.mark.django_db
def test_search_default_sort_without_query(api):
    cat = Category.objects.create(name="X", slug="x")
    brand = Brand.objects.create(name="Y", slug="y")
    Product.objects.create(
        name="Popular Item",
        slug="popular-item",
        short_description="",
        description="",
        category=cat,
        brand=brand,
        price="10.00",
        rating="4.0",
        review_count=1,
        stock_quantity=1,
        is_active=True,
        popularity_score=999,
    )
    url = reverse("search")
    r = api.get(url)
    assert r.status_code == 200
    assert r.data["sort"] == "popularity_desc"


@pytest.mark.django_db
def test_search_log_endpoint(api):
    url = reverse("search-log")
    r = api.post(
        url,
        {"query": "laptop", "result_count": 3},
        format="json",
    )
    assert r.status_code == 201
