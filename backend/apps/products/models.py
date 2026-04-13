from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:255]
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:255]
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=500, db_index=True)
    slug = models.SlugField(max_length=500, unique=True, db_index=True)
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.PROTECT,
        db_index=True,
    )
    brand = models.ForeignKey(
        Brand,
        related_name="products",
        on_delete=models.PROTECT,
        db_index=True,
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, db_index=True)
    review_count = models.PositiveIntegerField(default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    popularity_score = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-popularity_score", "-created_at"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["brand", "is_active"]),
            models.Index(fields=["price"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["is_active", "popularity_score"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:450]
            self.slug = base or "product"
        super().save(*args, **kwargs)
        dup = (
            Product.objects.filter(slug=self.slug)
            .exclude(pk=self.pk)
            .exists()
        )
        if dup:
            suffix = f"-{self.pk}"
            self.slug = (self.slug[: 500 - len(suffix)] + suffix)[:500]
            Product.objects.filter(pk=self.pk).update(slug=self.slug)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image_url = models.URLField(max_length=2048)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "id"]


class ProductTag(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="tags",
        on_delete=models.CASCADE,
    )
    tag = models.CharField(max_length=100, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["tag"]),
        ]
        unique_together = [["product", "tag"]]


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="attributes",
        on_delete=models.CASCADE,
    )
    attribute_name = models.CharField(max_length=255)
    attribute_value = models.CharField(max_length=500)
