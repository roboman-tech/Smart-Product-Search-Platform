import { apiClient } from "./client";

export async function logSearch(
  query: string,
  resultCount: number,
  userIdentifier?: string | null
): Promise<void> {
  await apiClient.post("/api/search/log/", {
    query,
    result_count: resultCount,
    user_identifier: userIdentifier ?? undefined,
  });
}

export async function logProductView(
  productId: number,
  opts?: { user_identifier?: string | null; session_id?: string | null }
): Promise<void> {
  await apiClient.post(`/api/products/${productId}/view/`, {
    user_identifier: opts?.user_identifier ?? undefined,
    session_id: opts?.session_id ?? undefined,
  });
}

export async function logRecommendationClick(
  sourceProductId: number,
  recommendedProductId: number,
  userIdentifier?: string | null
): Promise<void> {
  await apiClient.post("/api/recommendations/click/", {
    source_product: sourceProductId,
    recommended_product: recommendedProductId,
    user_identifier: userIdentifier ?? undefined,
  });
}
