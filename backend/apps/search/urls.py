from django.urls import path

from apps.search.views import SearchLogView, SearchView

urlpatterns = [
    path("", SearchView.as_view(), name="search"),
    path("log/", SearchLogView.as_view(), name="search-log"),
]
