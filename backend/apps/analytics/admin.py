from django.contrib import admin

from apps.analytics.models import ProductView, RecommendationClick, SearchLog


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("query", "result_count", "user_identifier", "created_at")
    search_fields = ("query", "user_identifier")
    list_filter = ("created_at",)


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ("product", "user_identifier", "session_id", "created_at")
    search_fields = ("product__name", "user_identifier", "session_id")
    list_filter = ("created_at",)


@admin.register(RecommendationClick)
class RecommendationClickAdmin(admin.ModelAdmin):
    list_display = (
        "source_product",
        "recommended_product",
        "user_identifier",
        "created_at",
    )
    search_fields = ("user_identifier",)
    list_filter = ("created_at",)
