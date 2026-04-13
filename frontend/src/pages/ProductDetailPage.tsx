import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { logProductView, logRecommendationClick } from "../api/analytics";
import Badge from "../components/Badge";
import ErrorMessage from "../components/ErrorMessage";
import Loader from "../components/Loader";
import ProductImageGallery from "../components/ProductImageGallery";
import RecommendationSection from "../components/RecommendationSection";
import StarRating from "../components/StarRating";
import { useProductDetail } from "../hooks/useProductDetail";
import { formatPrice } from "../utils/formatters";

function getOrCreateSessionId(): string {
  const KEY = "ssp_session";
  let id = sessionStorage.getItem(KEY);
  if (!id) {
    id = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    sessionStorage.setItem(KEY, id);
  }
  return id;
}

type Tab = "description" | "specifications";

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const productId = id ? parseInt(id, 10) : undefined;
  const { product, related, recommended, loading, error } = useProductDetail(productId);
  const [activeTab, setActiveTab] = useState<Tab>("description");

  useEffect(() => {
    if (product) {
      void logProductView(product.id, { session_id: getOrCreateSessionId() }).catch(() => {});
    }
  }, [product?.id]);

  const handleRecommendationClick = (targetId: number) => {
    if (product) {
      void logRecommendationClick(product.id, targetId).catch(() => {});
    }
  };

  /* ── Loading ─────────────────────────────────────────────────────── */
  if (loading) {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center">
        <Loader size="lg" label="Loading product…" />
      </div>
    );
  }

  /* ── Error / not found ───────────────────────────────────────────── */
  if (error || !product) {
    return (
      <div className="min-h-screen bg-canvas flex items-center justify-center px-4">
        <ErrorMessage
          title={error?.message.includes("404") ? "Product not found" : "Failed to load"}
          message={
            error?.message.includes("404")
              ? "This product may have been removed or the URL is incorrect."
              : error?.message ?? "An unexpected error occurred."
          }
          onRetry={() => navigate(-1)}
        />
      </div>
    );
  }

  const displayPrice = product.discount_price ?? product.price;
  const hasDiscount  = product.discount_price && Number(product.discount_price) < Number(product.price);
  const saveAmount   = hasDiscount
    ? Number(product.price) - Number(product.discount_price)
    : null;
  const discountPct  = hasDiscount
    ? Math.round(((Number(product.price) - Number(product.discount_price!)) / Number(product.price)) * 100)
    : null;
  const rating       = Number(product.rating);
  const inStock      = product.stock_quantity > 0;

  return (
    <div className="min-h-screen bg-canvas">
      <div className="max-w-screen-xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">

        {/* ── Breadcrumb ─────────────────────────────────────────── */}
        <nav className="flex items-center gap-2 text-xs text-muted mb-8" aria-label="Breadcrumb">
          <Link to="/" className="hover:text-ink transition-colors">Home</Link>
          <span className="text-faint">›</span>
          <Link to="/search" className="hover:text-ink transition-colors">Products</Link>
          {product.category?.name && (
            <>
              <span className="text-faint">›</span>
              <Link
                to={`/search?category=${encodeURIComponent(product.category.name)}`}
                className="hover:text-ink transition-colors"
              >
                {product.category.name}
              </Link>
            </>
          )}
          <span className="text-faint">›</span>
          <span className="text-text truncate max-w-[200px]">{product.name}</span>
        </nav>

        {/* ── Main layout ────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_1fr] gap-12 mb-16">
          {/* Left: Image gallery */}
          <ProductImageGallery
            images={product.images || []}
            productName={product.name}
          />

          {/* Right: Product info */}
          <div className="flex flex-col">
            {/* Brand + badges */}
            <div className="flex items-center justify-between gap-3 mb-3">
              {product.brand?.name && (
                <Link
                  to={`/search?brand=${encodeURIComponent(product.brand.name)}`}
                  className="text-xs font-bold text-brand-soft/70 uppercase tracking-widest hover:text-brand-soft transition-colors"
                >
                  {product.brand.name}
                </Link>
              )}
              <div className="flex items-center gap-2">
                <Badge variant={inStock ? "success" : "danger"} size="sm">
                  <span className={`inline-block w-1.5 h-1.5 rounded-full mr-1.5 ${inStock ? "bg-success animate-pulse" : "bg-danger"}`} />
                  {inStock ? "In Stock" : "Out of Stock"}
                </Badge>
                {discountPct && (
                  <Badge variant="danger" size="sm">-{discountPct}%</Badge>
                )}
              </div>
            </div>

            {/* Title */}
            <h1 className="text-2xl sm:text-3xl font-black text-ink leading-tight mb-4">
              {product.name}
            </h1>

            {/* Rating row */}
            {rating > 0 && (
              <div className="flex items-center gap-3 mb-5">
                <StarRating rating={rating} count={product.review_count} size="md" />
                <span className="text-xs text-faint">·</span>
                <span className="text-xs text-muted">{product.review_count} reviews</span>
              </div>
            )}

            {/* Short description */}
            {product.short_description && (
              <p className="text-sm text-muted leading-relaxed mb-6">
                {product.short_description}
              </p>
            )}

            {/* Price block */}
            <div className="p-5 rounded-2xl bg-raised border border-line mb-6">
              <div className="flex items-end gap-3 mb-2">
                <span className="text-3xl font-black text-ink">{formatPrice(displayPrice)}</span>
                {hasDiscount && (
                  <span className="text-base text-muted line-through pb-0.5">{formatPrice(product.price)}</span>
                )}
              </div>
              {saveAmount && saveAmount > 0 && (
                <p className="text-sm text-success font-semibold">
                  You save {formatPrice(saveAmount)} ({discountPct}% off)
                </p>
              )}
              {/* Stock count hint */}
              {inStock && product.stock_quantity < 10 && (
                <p className="text-xs text-warning mt-2">
                  Only {product.stock_quantity} left in stock — order soon
                </p>
              )}
            </div>

            {/* Tags */}
            {product.tags && product.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-6">
                {product.tags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => navigate(`/search?q=${encodeURIComponent(tag)}`)}
                    className="px-3 py-1 rounded-full text-xs font-medium bg-raised border border-line
                               text-muted hover:border-brand/40 hover:text-ink hover:bg-brand/8 transition-all"
                  >
                    #{tag}
                  </button>
                ))}
              </div>
            )}

            {/* Key highlights (from attributes) */}
            {product.attributes && product.attributes.length > 0 && (
              <div className="space-y-2.5">
                <p className="text-xs font-bold text-muted uppercase tracking-widest mb-3">Highlights</p>
                {product.attributes.slice(0, 4).map((attr) => (
                  <div key={attr.attribute_name} className="flex items-center gap-3 text-sm">
                    <svg className="w-4 h-4 text-brand-soft shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    <span className="text-muted">{attr.attribute_name}:</span>
                    <span className="text-text font-medium">{attr.attribute_value}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ── Tabs: Description / Specifications ──────────────────── */}
        <div className="mb-16">
          {/* Tab bar */}
          <div className="flex border-b border-line mb-8">
            {(["description", "specifications"] as Tab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-5 pb-4 pt-2 text-sm font-semibold capitalize transition-colors ${
                  activeTab === tab ? "tab-active" : "text-muted hover:text-ink"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {activeTab === "description" && (
            <div className="max-w-3xl">
              {product.description ? (
                <p className="text-text leading-relaxed whitespace-pre-line">
                  {product.description}
                </p>
              ) : (
                <p className="text-muted italic">No description available.</p>
              )}
            </div>
          )}

          {activeTab === "specifications" && (
            <div className="max-w-3xl">
              {product.attributes && product.attributes.length > 0 ? (
                <div className="rounded-2xl border border-line overflow-hidden">
                  {product.attributes.map((attr, i) => (
                    <div
                      key={attr.attribute_name}
                      className={`flex items-center px-5 py-3.5 text-sm gap-4 ${
                        i % 2 === 0 ? "bg-surface" : "bg-raised/50"
                      }`}
                    >
                      <span className="w-1/3 text-muted font-medium shrink-0">{attr.attribute_name}</span>
                      <span className="text-text">{attr.attribute_value}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted italic">No specifications available.</p>
              )}
            </div>
          )}
        </div>

        {/* ── Related products ─────────────────────────────────────── */}
        {related.length > 0 && (
          <div className="mb-16">
            <RecommendationSection
              title="Related Products"
              products={related}
              onProductClick={handleRecommendationClick}
              layout="scroll"
            />
          </div>
        )}

        {/* ── Recommended ──────────────────────────────────────────── */}
        {recommended.length > 0 && (
          <div className="pt-8 border-t border-line">
            <RecommendationSection
              title="You Might Also Like"
              products={recommended}
              onProductClick={handleRecommendationClick}
              layout="grid"
            />
          </div>
        )}
      </div>
    </div>
  );
}
