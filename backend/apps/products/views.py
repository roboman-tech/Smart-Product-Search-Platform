"""HTTP adapters for catalog endpoints; business logic lives in ``services`` / ``catalog_service``."""

from __future__ import annotations

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.serializers import ProductViewCreateSerializer
from apps.analytics.services import create_product_view_record
from apps.products.catalog_service import (
    get_product_detail_payload,
    get_related_products_payload,
    get_recommendations_payload,
    list_brands_payload,
    list_categories_payload,
)
from apps.products.serializers import ProductListSerializer
from apps.products.services import build_product_list_queryset
from ecommerce.pagination import ProductPagination


class CategoryListView(APIView):
    def get(self, request):
        return Response(list_categories_payload())


class BrandListView(APIView):
    def get(self, request):
        return Response(list_brands_payload())


class ProductListView(ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        return build_product_list_queryset(self.request.query_params)


class ProductDetailView(APIView):
    def get(self, request, pk):
        return Response(get_product_detail_payload(int(pk)))


class ProductRelatedView(APIView):
    def get(self, request, pk):
        return Response(get_related_products_payload(int(pk)))


class ProductRecommendationsView(APIView):
    def get(self, request, pk):
        return Response(get_recommendations_payload(int(pk)))


class ProductViewLogView(APIView):
    def post(self, request, pk):
        serializer = ProductViewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_product_view_record(
            product_id=int(pk),
            user_identifier=serializer.validated_data.get("user_identifier") or None,
            session_id=serializer.validated_data.get("session_id") or None,
        )
        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
