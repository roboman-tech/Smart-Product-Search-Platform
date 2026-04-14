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
 *
 * Fetches are kept independent: a failure on one endpoint does not prevent the
 * other from populating. This avoids the previous Promise.all pattern where a
 * CORS/network error on /api/categories/ would silently clear brands too.
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

    const catPromise = fetchCategories()
      .then((cats) => {
        if (!cancelled) setCategories(cats);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          const err = e instanceof Error ? e : new Error("Failed to load categories");
          console.error("[useCatalogMeta] categories:", err.message);
          setError(err);
        }
      });

    const brandPromise = fetchBrands()
      .then((brs) => {
        if (!cancelled) setBrands(brs);
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          const err = e instanceof Error ? e : new Error("Failed to load brands");
          console.error("[useCatalogMeta] brands:", err.message);
          setError(err);
        }
      });

    Promise.allSettled([catPromise, brandPromise]).finally(() => {
      if (!cancelled) setLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, []);

  return { categories, brands, loading, error };
}
