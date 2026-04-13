import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.products.models import Brand, Category, Product


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
def test_related_and_recommendations(api):
    cat = Category.objects.create(name="Audio", slug="audio")
    brand = Brand.objects.create(name="SoundMax", slug="soundmax")
    p1 = Product.objects.create(
        name="Headphones A",
        slug="headphones-a",
        short_description="",
        description="",
        category=cat,
        brand=brand,
        price="100.00",
        rating="4.5",
        review_count=10,
        stock_quantity=5,
        is_active=True,
        popularity_score=50,
    )
    Product.objects.create(
        name="Headphones B",
        slug="headphones-b",
        short_description="",
        description="",
        category=cat,
        brand=brand,
        price="120.00",
        rating="4.2",
        review_count=8,
        stock_quantity=2,
        is_active=True,
        popularity_score=40,
    )

    rel = api.get(reverse("product-related", kwargs={"pk": p1.pk}))
    assert rel.status_code == 200
    assert isinstance(rel.data, list)

    rec = api.get(reverse("product-recommendations", kwargs={"pk": p1.pk}))
    assert rec.status_code == 200


@pytest.mark.django_db
def test_recommendation_click(api):
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
