import type { PaginatedProducts } from "../types/api";
import type { Brand, Category, ProductDetail, ProductListItem } from "../types/product";
import { apiClient } from "./client";

export interface ProductListParams {
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

function cleanParams(
  params: ProductListParams
): Record<string, string> | undefined {
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== ""
  ) as [string, string][];
  if (entries.length === 0) {
    return undefined;
  }
  return Object.fromEntries(entries);
}

export async function fetchCategories(): Promise<Category[]> {
  const { data } = await apiClient.get<Category[]>("/api/categories/");
  return data;
}

export async function fetchBrands(): Promise<Brand[]> {
  const { data } = await apiClient.get<Brand[]>("/api/brands/");
  return data;
}

export async function fetchProducts(
  params: ProductListParams
): Promise<PaginatedProducts> {
  const { data } = await apiClient.get<PaginatedProducts>("/api/products/", {
    params: cleanParams(params),
  });
  return data;
}

export async function fetchProductDetail(id: number): Promise<ProductDetail> {
  const { data } = await apiClient.get<ProductDetail>(`/api/products/${id}/`);
  return data;
}

export async function fetchRelatedProducts(
  id: number
): Promise<ProductListItem[]> {
  const { data } = await apiClient.get<ProductListItem[]>(
    `/api/products/${id}/related/`
  );
  return data;
}

export async function fetchRecommendations(
  id: number
): Promise<ProductListItem[]> {
  const { data } = await apiClient.get<ProductListItem[]>(
    `/api/products/${id}/recommendations/`
  );
  return data;
}
