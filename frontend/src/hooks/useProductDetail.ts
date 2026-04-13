import { useEffect, useState } from "react";
import {
  fetchProductDetail,
  fetchRecommendations,
  fetchRelatedProducts,
} from "../api/products";
import type { ProductDetail, ProductListItem } from "../types/product";

export interface UseProductDetailResult {
  product: ProductDetail | null;
  related: ProductListItem[];
  recommended: ProductListItem[];
  loading: boolean;
  error: Error | null;
}

export function useProductDetail(
  id: number | undefined
): UseProductDetailResult {
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [related, setRelated] = useState<ProductListItem[]>([]);
  const [recommended, setRecommended] = useState<ProductListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (id === undefined || Number.isNaN(id)) {
      setProduct(null);
      setRelated([]);
      setRecommended([]);
      setLoading(false);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([
      fetchProductDetail(id),
      fetchRelatedProducts(id),
      fetchRecommendations(id),
    ])
      .then(([p, r, rec]) => {
        if (!cancelled) {
          setProduct(p);
          setRelated(r);
          setRecommended(rec);
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(
            e instanceof Error ? e : new Error("Failed to load product")
          );
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  return { product, related, recommended, loading, error };
}
