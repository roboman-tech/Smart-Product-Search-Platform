"""Persistence helpers for analytics events (search, views, recommendation clicks)."""

from __future__ import annotations

from django.shortcuts import get_object_or_404

from apps.analytics.models import ProductView, RecommendationClick, SearchLog
from apps.products.models import Product


def create_search_log_record(
    *,
    query: str,
    result_count: int,
    user_identifier: str | None,
) -> SearchLog:
    return SearchLog.objects.create(
        query=query,
        result_count=result_count,
        user_identifier=user_identifier,
    )


def create_product_view_record(
    *,
    product_id: int,
    user_identifier: str | None,
    session_id: str | None,
) -> ProductView:
    get_object_or_404(Product, pk=product_id, is_active=True)
    return ProductView.objects.create(
        product_id=product_id,
        user_identifier=user_identifier,
        session_id=session_id,
    )


def create_recommendation_click_record(
    *,
    source_product_id: int,
    recommended_product_id: int,
    user_identifier: str | None,
) -> RecommendationClick:
    get_object_or_404(Product, pk=source_product_id, is_active=True)
    get_object_or_404(Product, pk=recommended_product_id, is_active=True)
    return RecommendationClick.objects.create(
        source_product_id=source_product_id,
        recommended_product_id=recommended_product_id,
        user_identifier=user_identifier,
    )
