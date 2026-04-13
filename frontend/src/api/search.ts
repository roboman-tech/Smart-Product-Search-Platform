import type { SearchResponse } from "../types/api";
import { apiClient } from "./client";

export interface SearchParams {
  q?: string;
  category?: string;
  brand?: string;
  min_price?: string;
  max_price?: string;
  rating?: string;
  in_stock?: string;
  sort?: string;
  page?: string;
  page_size?: string;
}

export async function searchProducts(
  params: Record<string, string>
): Promise<SearchResponse> {
  const { data } = await apiClient.get<SearchResponse>("/api/search/", {
    params,
  });
  return data;
}
