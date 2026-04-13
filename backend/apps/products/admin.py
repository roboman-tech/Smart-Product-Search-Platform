from django.contrib import admin
from django.utils.text import slugify

from apps.products.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductImage,
    ProductTag,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductTagInline(admin.TabularInline):
    model = ProductTag
    extra = 1


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("parent",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "category",
        "brand",
        "price",
        "rating",
        "stock_quantity",
        "is_active",
        "popularity_score",
    )
    list_filter = ("is_active", "category", "brand")
    search_fields = ("name", "slug", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (ProductImageInline, ProductTagInline, ProductAttributeInline)
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)[:500]
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image_url", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("product__name",)


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ("product", "tag")
    search_fields = ("tag", "product__name")


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("product", "attribute_name", "attribute_value")
    search_fields = ("attribute_name", "product__name")
