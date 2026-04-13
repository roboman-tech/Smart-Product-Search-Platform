"""Recommendation click logging; persistence in ``apps.analytics.services``."""

from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.serializers import RecommendationClickCreateSerializer
from apps.analytics.services import create_recommendation_click_record


class RecommendationClickView(APIView):
    def post(self, request):
        serializer = RecommendationClickCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_recommendation_click_record(
            source_product_id=serializer.validated_data["source_product"],
            recommended_product_id=serializer.validated_data["recommended_product"],
            user_identifier=serializer.validated_data.get("user_identifier") or None,
        )
        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
