import { Link } from "react-router-dom";
import { cn } from "../lib/cn";
import type { ProductListItem } from "../types/product";
import { formatPrice } from "../utils/formatters";
import Badge from "./Badge";
import StarRating from "./StarRating";

interface ProductCardProps {
  product: ProductListItem;
  className?: string;
  style?: React.CSSProperties;
}

function DiscountBadge({
  price,
  discountPrice,
}: {
  price: string | number;
  discountPrice: string | number | null;
}) {
  if (!discountPrice) return null;
  const orig = Number(price);
  const sale = Number(discountPrice);
  if (!sale || sale >= orig) return null;
  const pct = Math.round(((orig - sale) / orig) * 100);
  if (pct < 1) return null;
  return (
    <div className="absolute top-3 left-3 z-10 px-2.5 py-0.5 rounded-full text-[10px] font-bold
                    bg-danger text-white shadow-md shadow-danger/30">
      -{pct}%
    </div>
  );
}

export default function ProductCard({ product, className, style }: ProductCardProps) {
  const inStock = product.stock_quantity > 0;
  const salePrice = product.discount_price;
  const displayPrice = salePrice ?? product.price;
  const rating = Number(product.rating);

  return (
    <Link
      to={`/products/${product.id}`}
      style={style}
      className={cn("group block card overflow-hidden p-0", className)}
      aria-label={product.name}
    >
      {/* Image */}
      <div className="relative overflow-hidden aspect-square bg-raised">
        {product.primary_image ? (
          <img
            src={product.primary_image}
            alt={product.name}
            loading="lazy"
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <svg className="w-12 h-12 text-faint" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 19.5h18M3 4.5h18" />
            </svg>
          </div>
        )}
        {/* Hover overlay */}
        <div className="absolute inset-x-0 bottom-0 h-1/3 bg-gradient-to-t from-surface/60 to-transparent
                        opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        <DiscountBadge price={product.price} discountPrice={salePrice} />
        {/* Stock dot */}
        <div className={cn(
          "absolute top-3 right-3 z-10 w-2.5 h-2.5 rounded-full border-2 border-raised",
          inStock ? "bg-success" : "bg-danger",
        )} />
      </div>

      {/* Content */}
      <div className="p-4">
        {product.brand?.name && (
          <p className="text-[10px] font-semibold text-brand-soft/60 uppercase tracking-widest mb-1.5 truncate">
            {product.brand.name}
          </p>
        )}
        <h3 className="text-sm font-semibold text-text leading-snug line-clamp-2 mb-2.5
                       group-hover:text-ink transition-colors">
          {product.name}
        </h3>
        {rating > 0 && (
          <StarRating rating={rating} count={product.review_count} size="sm" className="mb-2.5" />
        )}

        {/* Category */}
        {product.category?.name && (
          <div className="mb-2.5">
            <Badge variant="neutral" size="sm">
              {product.category.name}
            </Badge>
          </div>
        )}

        {/* Price */}
        <div className="flex items-center gap-2">
          <span className="text-base font-bold text-ink">{formatPrice(displayPrice)}</span>
          {salePrice && (
            <span className="text-xs text-muted line-through">{formatPrice(product.price)}</span>
          )}
        </div>
      </div>
    </Link>
  );
}
