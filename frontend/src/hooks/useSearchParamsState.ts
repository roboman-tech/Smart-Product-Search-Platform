import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import {
  paramsToSearchState,
  searchStateToParams,
  type SearchState,
} from "../utils/queryParams";

/** Changing these resets pagination to page 1. */
const RESET_PAGE_KEYS = [
  "q",
  "category",
  "brand",
  "min_price",
  "max_price",
  "rating",
  "in_stock",
  "sort",
] as const;

export function useSearchParamsState() {
  const [searchParams, setSearchParams] = useSearchParams();

  const state = useMemo(
    () => paramsToSearchState(searchParams),
    [searchParams]
  );

  const setState = useCallback(
    (next: SearchState | ((prev: SearchState) => SearchState)) => {
      setSearchParams((prev) => {
        const current = paramsToSearchState(prev);
        const resolved = typeof next === "function" ? next(current) : next;
        return searchStateToParams(resolved);
      });
    },
    [setSearchParams]
  );

  const patchState = useCallback(
    (patch: Partial<SearchState>) => {
      setState((prev) => {
        const merged: SearchState = { ...prev, ...patch };
        if (RESET_PAGE_KEYS.some((k) => k in patch)) {
          merged.page = "1";
        }
        return merged;
      });
    },
    [setState]
  );

  return { state, setState, patchState, searchParams };
}
