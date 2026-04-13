/**
 * Single source of truth for URL query keys used on `/search` and API calls.
 */
export const SEARCH_PARAM_KEYS = [
  "q",
  "category",
  "brand",
  "min_price",
  "max_price",
  "rating",
  "in_stock",
  "sort",
  "page",
  "page_size",
] as const;

export type SearchParamKey = (typeof SEARCH_PARAM_KEYS)[number];

export type SearchState = Partial<Record<SearchParamKey, string>>;
