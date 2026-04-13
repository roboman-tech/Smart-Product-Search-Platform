import type { ProductListItem } from "./product";

export interface PaginatedProducts {
  count: number;
  next: string | null;
  previous: string | null;
  results: ProductListItem[];
}

export interface SearchResponse {
  query: string;
  total: number;
  page: number;
  page_size: number;
  sort: string;
  results: ProductListItem[];
}
