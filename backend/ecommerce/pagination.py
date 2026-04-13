from __future__ import annotations

from typing import Mapping

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

from ecommerce.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


def parse_page_params(query_params: Mapping[str, str | None]) -> tuple[int, int]:
    """Parse ``page`` and ``page_size`` from query string with validation."""
    raw_page = query_params.get("page") or "1"
    raw_size = query_params.get("page_size") or str(DEFAULT_PAGE_SIZE)
    try:
        page = int(raw_page)
        page_size = int(raw_size)
    except (TypeError, ValueError):
        raise ValidationError({"page": "Invalid pagination parameters."})
    if page < 1 or page_size < 1:
        raise ValidationError({"page": "page and page_size must be positive."})
    if page_size > MAX_PAGE_SIZE:
        raise ValidationError(
            {"page_size": f"page_size cannot exceed {MAX_PAGE_SIZE}."}
        )
    return page, page_size


class ProductPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = MAX_PAGE_SIZE

    def paginate_queryset(self, queryset, request, view=None):
        page = request.query_params.get(self.page_query_param)
        page_size = request.query_params.get(self.page_size_query_param)
        if page is not None:
            try:
                p = int(page)
                if p < 1:
                    raise ValidationError({"page": "Must be a positive integer."})
            except ValueError:
                raise ValidationError({"page": "Invalid page."})
        if page_size is not None:
            try:
                ps = int(page_size)
                if ps < 1:
                    raise ValidationError({"page_size": "Must be a positive integer."})
            except ValueError:
                raise ValidationError({"page_size": "Invalid page_size."})
        return super().paginate_queryset(queryset, request, view)
