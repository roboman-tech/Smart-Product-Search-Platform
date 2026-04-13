import { Link } from "react-router-dom";
import { cn } from "../lib/cn";
import type { ProductListItem } from "../types/product";
import { formatPrice } from "../utils/formatters";
import StarRating from "./StarRating";

interface RecommendationSectionProps {
  title: string;
  products: ProductListItem[];
  onProductClick?: (productId: number) => void;
  layout?: "scroll" | "grid";
  className?: string;
}

function ProductTile({
  product,
  onClick,
  compact,
}: {
  product: ProductListItem;
  onClick?: () => void;
  compact?: boolean;
}) {
  const displayPrice = product.discount_price ?? product.price;
  const rating = Number(product.rating);

  return (
    <Link
      to={`/products/${product.id}`}
      onClick={onClick}
      className={cn(
        "group card overflow-hidden p-0",
        compact ? "shrink-0 w-44" : "",
      )}
      aria-label={product.name}
    >
      <div className="relative aspect-square bg-raised overflow-hidden">
        {product.primary_image ? (
          <img
            src={product.primary_image}
            alt={product.name}
            loading="lazy"
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <svg className="w-8 h-8 text-faint" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909" />
            </svg>
          </div>
        )}
      </div>
      <div className="p-3">
        {product.brand?.name && (
          <p className="text-[9px] text-brand-soft/60 uppercase tracking-widest mb-1 truncate font-semibold">
            {product.brand.name}
          </p>
        )}
        <p className={cn(
          "font-semibold text-text line-clamp-2 leading-snug mb-2 group-hover:text-ink transition-colors",
          compact ? "text-xs" : "text-sm",
        )}>
          {product.name}
        </p>
        {rating > 0 && (
          <StarRating rating={rating} size="sm" showCount={false} className="mb-1.5" />
        )}
        <p className={cn("font-bold text-ink", compact ? "text-sm" : "text-base")}>
          {formatPrice(displayPrice)}
        </p>
      </div>
    </Link>
  );
}

export default function RecommendationSection({
  title,
  products,
  onProductClick,
  layout = "scroll",
  className,
}: RecommendationSectionProps) {
  if (products.length === 0) return null;

  return (
    <section className={cn("", className)}>
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-bold text-ink">{title}</h2>
        <span className="text-xs text-muted bg-raised border border-line rounded-full px-3 py-1">
          {products.length} items
        </span>
      </div>

      {layout === "scroll" ? (
        <div className="scroll-row">
          {products.map((p) => (
            <ProductTile
              key={p.id}
              product={p}
              compact
              onClick={onProductClick ? () => onProductClick(p.id) : undefined}
            />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {products.map((p) => (
            <ProductTile
              key={p.id}
              product={p}
              onClick={onProductClick ? () => onProductClick(p.id) : undefined}
            />
          ))}
        </div>
      )}
    </section>
  );
}
