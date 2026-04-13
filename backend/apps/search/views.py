"""Search HTTP endpoints; orchestration is in ``apps.search.services``."""

from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.serializers import SearchLogCreateSerializer
from apps.analytics.services import create_search_log_record
from apps.search.services import search_products


class SearchView(APIView):
    def get(self, request):
        return Response(search_products(request.query_params))


class SearchLogView(APIView):
    def post(self, request):
        serializer = SearchLogCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_search_log_record(
            query=serializer.validated_data["query"],
            result_count=serializer.validated_data["result_count"],
            user_identifier=serializer.validated_data.get("user_identifier") or None,
        )
        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
