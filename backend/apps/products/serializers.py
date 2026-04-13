from rest_framework import serializers

from apps.products.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductImage,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent")


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug")


class BrandMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name")


class CategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")


class ProductListSerializer(serializers.ModelSerializer):
    brand = BrandMiniSerializer(read_only=True)
    category = CategoryMiniSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "price",
            "discount_price",
            "rating",
            "review_count",
            "stock_quantity",
            "brand",
            "category",
            "primary_image",
        )

    def get_primary_image(self, obj: Product) -> str | None:
        imgs = getattr(obj, "_prefetched_objects_cache", {}).get("images")
        if imgs is not None:
            ordered = sorted(imgs, key=lambda i: (not i.is_primary, i.id))
            return ordered[0].image_url if ordered else None
        img = obj.images.order_by("-is_primary", "id").first()
        return img.image_url if img else None


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image_url", "is_primary")


class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ("attribute_name", "attribute_value")


class ProductDetailSerializer(serializers.ModelSerializer):
    brand = BrandMiniSerializer(read_only=True)
    category = CategoryMiniSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()
    attributes = ProductAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "short_description",
            "description",
            "price",
            "discount_price",
            "rating",
            "review_count",
            "stock_quantity",
            "is_active",
            "brand",
            "category",
            "images",
            "tags",
            "attributes",
        )

    def get_tags(self, obj: Product) -> list[str]:
        tags = getattr(obj, "_prefetched_objects_cache", {}).get("tags")
        if tags is not None:
            return [t.tag for t in sorted(tags, key=lambda x: x.tag)]
        return list(obj.tags.order_by("tag").values_list("tag", flat=True))
