from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.products.urls")),
    path("api/search/", include("apps.search.urls")),
    path("api/recommendations/", include("apps.recommendations.urls")),
]
