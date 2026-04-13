from django.db.models import Prefetch, QuerySet

from apps.products.models import Product, ProductImage, ProductTag


def _primary_image_url(p: Product) -> str | None:
    imgs = list(p.images.all())
    if not imgs:
        return None
    primary = next((i for i in imgs if i.is_primary), imgs[0])
    return primary.image_url


def _product_card_dict(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "price": float(p.price),
        "discount_price": float(p.discount_price) if p.discount_price is not None else None,
        "rating": float(p.rating),
        "review_count": p.review_count,
        "stock_quantity": p.stock_quantity,
        "brand": {"id": p.brand_id, "name": p.brand.name},
        "category": {"id": p.category_id, "name": p.category.name},
        "primary_image": _primary_image_url(p),
    }


def _base_candidates(source: Product, limit: int = 80) -> QuerySet[Product]:
    return (
        Product.objects.filter(is_active=True)
        .exclude(pk=source.pk)
        .select_related("category", "brand")
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.order_by("-is_primary", "id"),
            ),
            Prefetch("tags", queryset=ProductTag.objects.order_by("tag")),
        )
        .order_by("-popularity_score", "-rating")[:limit]
    )


def _score_related(source: Product, candidate: Product, source_tags: set[str]) -> float:
    score = 0.0
    if candidate.category_id == source.category_id:
        score += 400
    cand_tags = {t.tag.lower() for t in candidate.tags.all()}
    shared = len(source_tags & cand_tags)
    score += shared * 120
    if candidate.brand_id == source.brand_id:
        score += 200
    if candidate.stock_quantity > 0:
        score += 80
    score += float(candidate.rating) * 15
    score += min(candidate.popularity_score, 500) * 0.2
    return score


def get_related_products(source: Product, limit: int = 10) -> list[dict]:
    source_tags = {t.tag.lower() for t in source.tags.all()}
    candidates = list(_base_candidates(source, limit=120))
    scored: list[tuple[float, Product]] = []
    for c in candidates:
        scored.append((_score_related(source, c, source_tags), c))
    scored.sort(key=lambda x: (-x[0], -float(x[1].rating), -x[1].popularity_score))
    return [_product_card_dict(p) for _, p in scored[:limit]]


def get_recommendations(source: Product, limit: int = 12) -> list[dict]:
    """Rule-based: same category, tag overlap, same brand, popularity/rating."""
    source_tags = {t.tag.lower() for t in source.tags.all()}
    qs = (
        Product.objects.filter(is_active=True, category_id=source.category_id)
        .exclude(pk=source.pk)
        .select_related("category", "brand")
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.order_by("-is_primary", "id"),
            ),
            Prefetch("tags", queryset=ProductTag.objects.order_by("tag")),
        )
    )
    pool: list[Product] = list(qs.order_by("-popularity_score")[:60])
    brand_pool = list(
        Product.objects.filter(is_active=True, brand_id=source.brand_id)
        .exclude(pk=source.pk)
        .select_related("category", "brand")
        .prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.order_by("-is_primary", "id"),
            ),
            Prefetch("tags", queryset=ProductTag.objects.order_by("tag")),
        )
        .order_by("-rating")[:30]
    )
    seen: set[int] = set()
    merged: list[Product] = []
    for p in pool + brand_pool:
        if p.id not in seen:
            seen.add(p.id)
            merged.append(p)

    def rec_score(p: Product) -> float:
        s = float(p.rating) * 20 + p.popularity_score * 0.3
        if p.brand_id == source.brand_id:
            s += 150
        cand_tags = {t.tag.lower() for t in p.tags.all()}
        s += len(source_tags & cand_tags) * 100
        if p.stock_quantity > 0:
            s += 50
        return s

    merged.sort(key=lambda p: -rec_score(p))
    return [_product_card_dict(p) for p in merged[:limit]]
