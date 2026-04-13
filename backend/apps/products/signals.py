from __future__ import annotations

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ecommerce.cache_service import (
    invalidate_brand_list_cache,
    invalidate_category_list_cache,
    invalidate_product_caches,
)

from apps.products.models import Brand, Category, Product


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def product_changed(sender, instance, **kwargs):
    invalidate_product_caches(instance.pk)


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def category_changed(sender, **kwargs):
    invalidate_category_list_cache()


@receiver(post_save, sender=Brand)
@receiver(post_delete, sender=Brand)
def brand_changed(sender, **kwargs):
    invalidate_brand_list_cache()
