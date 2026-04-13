"""Tests for shared pagination helpers."""

from __future__ import annotations

import pytest
from rest_framework.exceptions import ValidationError

from ecommerce.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from ecommerce.pagination import parse_page_params


def test_parse_page_params_defaults():
    page, size = parse_page_params({})
    assert page == 1
    assert size == DEFAULT_PAGE_SIZE


def test_parse_page_params_custom():
    page, size = parse_page_params({"page": "2", "page_size": "10"})
    assert page == 2
    assert size == 10


def test_parse_page_params_rejects_oversized_page_size():
    with pytest.raises(ValidationError):
        parse_page_params({"page_size": str(MAX_PAGE_SIZE + 1)})


def test_parse_page_params_rejects_invalid():
    with pytest.raises(ValidationError):
        parse_page_params({"page": "0"})
