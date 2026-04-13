import { useEffect, useState } from "react";
import { fetchBrands, fetchCategories } from "../api/products";
import type { Brand, Category } from "../types/product";

export interface UseCatalogMetaResult {
  categories: Category[];
  brands: Brand[];
  loading: boolean;
  error: Error | null;
}

/**
 * Loads category and brand lists for filter UI (cached heavily on the server).
 */
export function useCatalogMeta(): UseCatalogMetaResult {
  const [categories, setCategories] = useState<Category[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([fetchCategories(), fetchBrands()])
      .then(([cats, brs]) => {
        if (!cancelled) {
          setCategories(cats);
          setBrands(brs);
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(
            e instanceof Error ? e : new Error("Failed to load filter options")
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
  }, []);

  return { categories, brands, loading, error };
}
