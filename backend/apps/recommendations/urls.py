from django.urls import path

from apps.recommendations.views import RecommendationClickView

urlpatterns = [
    path("click/", RecommendationClickView.as_view(), name="recommendation-click"),
]
