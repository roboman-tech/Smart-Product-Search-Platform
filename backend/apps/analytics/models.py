from django.db import models


class SearchLog(models.Model):
    query = models.CharField(max_length=500, db_index=True)
    user_identifier = models.CharField(max_length=255, null=True, blank=True)
    result_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class ProductView(models.Model):
    product = models.ForeignKey(
        "products.Product",
        related_name="views",
        on_delete=models.CASCADE,
    )
    user_identifier = models.CharField(max_length=255, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]


class RecommendationClick(models.Model):
    source_product = models.ForeignKey(
        "products.Product",
        related_name="recommendation_clicks_as_source",
        on_delete=models.CASCADE,
    )
    recommended_product = models.ForeignKey(
        "products.Product",
        related_name="recommendation_clicks_as_target",
        on_delete=models.CASCADE,
    )
    user_identifier = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
