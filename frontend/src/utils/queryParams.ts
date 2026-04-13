import {
  SEARCH_PARAM_KEYS,
  type SearchParamKey,
  type SearchState,
} from "./searchParamsConfig";

export { SEARCH_PARAM_KEYS, type SearchParamKey, type SearchState };

export function searchStateToParams(state: SearchState): URLSearchParams {
  const p = new URLSearchParams();
  for (const key of SEARCH_PARAM_KEYS) {
    const v = state[key];
    if (v !== undefined && v !== "") {
      p.set(key, v);
    }
  }
  return p;
}

export function paramsToSearchState(params: URLSearchParams): SearchState {
  const s: SearchState = {};
  for (const key of SEARCH_PARAM_KEYS) {
    const v = params.get(key);
    if (v !== null && v !== "") {
      s[key] = v;
    }
  }
  return s;
}

const DEFAULT_PAGE = "1";
const DEFAULT_PAGE_SIZE = "20";

/**
 * Builds a plain object for GET /api/search/ (omits empty values; applies list defaults).
 */
export function searchStateToApiParams(state: SearchState): Record<string, string> {
  const out: Record<string, string> = {};
  for (const key of SEARCH_PARAM_KEYS) {
    const v = state[key];
    if (v !== undefined && v !== "") {
      out[key] = v;
    }
  }
  if (!out.page) {
    out.page = DEFAULT_PAGE;
  }
  if (!out.page_size) {
    out.page_size = DEFAULT_PAGE_SIZE;
  }
  return out;
}
