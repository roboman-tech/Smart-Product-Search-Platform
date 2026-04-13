import { useCallback, useEffect, useState } from "react";
import { fetchBrands, fetchCategories, fetchProducts } from "../api/products";
import type { Brand, Category, ProductListItem } from "../types/product";

export interface UseHomePageDataResult {
  categories: Category[];
  brands: Brand[];
  popular: ProductListItem[];
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useHomePageData(): UseHomePageDataResult {
  const [categories, setCategories] = useState<Category[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [popular, setPopular] = useState<ProductListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [cats, brs, prods] = await Promise.all([
        fetchCategories(),
        fetchBrands(),
        fetchProducts({ sort: "popularity_desc", page_size: "8" }),
      ]);
      setCategories(cats);
      setBrands(brs);
      setPopular(prods.results);
    } catch (e: unknown) {
      setError(e instanceof Error ? e : new Error("Failed to load home"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { categories, brands, popular, loading, error, refetch: load };
}
