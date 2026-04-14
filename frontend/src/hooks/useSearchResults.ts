import { useCallback, useEffect, useMemo, useState } from "react";
import { logSearch } from "../api/analytics";
import { searchProducts } from "../api/search";
import type { SearchResponse } from "../types/api";
import { searchStateToApiParams, type SearchState } from "../utils/queryParams";

export interface UseSearchResultsResult {
  data: SearchResponse | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

/**
 * Fetches `/api/search/` whenever URL-derived `state` changes; logs analytics on success.
 */
export function useSearchResults(state: SearchState): UseSearchResultsResult {
  const [data, setData] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const apiParams = useMemo(
    () => searchStateToApiParams(state),
    [
      state.q,
      state.category,
      state.brand,
      state.min_price,
      state.max_price,
      state.rating,
      state.in_stock,
      state.sort,
      state.page,
      state.page_size,
    ]
  );

  const run = useCallback(async () => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await searchProducts(apiParams);
      setData(res);
      // Pass `?? 0` so result_count is always a finite number, never undefined.
      void logSearch(
        res.query || state.q?.trim() || "",
        res.total ?? 0
      ).catch(() => {});
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Search failed"));
    } finally {
      setLoading(false);
    }
  }, [apiParams, state.q]);

  useEffect(() => {
    void run();
  }, [run]);

  return { data, loading, error, refetch: run };
}
