import { cn } from "../lib/cn";
import type { ProductListItem } from "../types/product";
import ProductCard from "./ProductCard";
import { SkeletonGrid } from "./SkeletonCard";

interface ProductGridProps {
  products: ProductListItem[];
  loading?: boolean;
  className?: string;
}

export default function ProductGrid({ products, loading = false, className }: ProductGridProps) {
  if (loading) {
    return <SkeletonGrid count={12} />;
  }

  return (
    <div
      className={cn(
        "grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 gap-4",
        className,
      )}
    >
      {products.map((product, i) => (
        <ProductCard
          key={product.id}
          product={product}
          className="animate-fade-up"
          style={{ animationDelay: `${i * 35}ms` } as React.CSSProperties}
        />
      ))}
    </div>
  );
}
