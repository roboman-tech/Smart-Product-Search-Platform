import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.products.models import Brand, Category, Product


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def sample_product(db):
    cat = Category.objects.create(name="Audio", slug="audio")
    brand = Brand.objects.create(name="SoundMax", slug="soundmax")
    return Product.objects.create(
        name="Wireless Headphones X1",
        slug="wireless-headphones-x1",
        short_description="Premium wireless headphones",
        description="Long description with bluetooth and battery details.",
        category=cat,
        brand=brand,
        price="149.99",
        discount_price="129.99",
        rating="4.6",
        review_count=310,
        stock_quantity=12,
        is_active=True,
        popularity_score=500,
    )


@pytest.mark.django_db
def test_product_list_filters_and_sort(api, sample_product):
    url = reverse("product-list")
    r = api.get(url)
    assert r.status_code == 200
    assert r.data["count"] >= 1

    r2 = api.get(url, {"category": "audio", "sort": "price_asc"})
    assert r2.status_code == 200

    r3 = api.get(url, {"sort": "not_a_sort"})
    assert r3.status_code == 400


@pytest.mark.django_db
def test_product_detail_404(api):
    r = api.get(reverse("product-detail", kwargs={"pk": 99999}))
    assert r.status_code == 404


@pytest.mark.django_db
def test_product_detail_ok(api, sample_product):
    r = api.get(reverse("product-detail", kwargs={"pk": sample_product.pk}))
    assert r.status_code == 200
    assert r.data["name"] == sample_product.name
    assert "tags" in r.data


@pytest.mark.django_db
def test_categories_and_brands_cached_shape(api, sample_product):
    c = api.get(reverse("category-list"))
    assert c.status_code == 200
    assert isinstance(c.data, list)
    b = api.get(reverse("brand-list"))
    assert b.status_code == 200


@pytest.mark.django_db
def test_min_price_validation(api):
    url = reverse("product-list")
    r = api.get(url, {"min_price": "100", "max_price": "50"})
    assert r.status_code == 400
