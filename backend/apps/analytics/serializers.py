from rest_framework import serializers


class SearchLogCreateSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=500)
    result_count = serializers.IntegerField(min_value=0)
    user_identifier = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )


class ProductViewCreateSerializer(serializers.Serializer):
    user_identifier = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
    session_id = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )


class RecommendationClickCreateSerializer(serializers.Serializer):
    source_product = serializers.IntegerField()
    recommended_product = serializers.IntegerField()
    user_identifier = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )
