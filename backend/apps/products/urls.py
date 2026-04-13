from django.urls import path

from apps.products.views import (
    BrandListView,
    CategoryListView,
    ProductDetailView,
    ProductListView,
    ProductRecommendationsView,
    ProductRelatedView,
    ProductViewLogView,
)

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("brands/", BrandListView.as_view(), name="brand-list"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path(
        "products/<int:pk>/related/",
        ProductRelatedView.as_view(),
        name="product-related",
    ),
    path(
        "products/<int:pk>/recommendations/",
        ProductRecommendationsView.as_view(),
        name="product-recommendations",
    ),
    path(
        "products/<int:pk>/view/",
        ProductViewLogView.as_view(),
        name="product-view-log",
    ),
]
