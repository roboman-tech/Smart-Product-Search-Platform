import { apiClient } from "./client";

export async function logSearch(
  query: string,
  resultCount: number,
  userIdentifier?: string | null
): Promise<void> {
  const q = typeof query === "string" ? query.trim() : "";
  const count = Number.isFinite(Number(resultCount)) ? Number(resultCount) : 0;

  // Backend requires a non-empty query — skip logging for blank searches.
  if (!q) return;

  await apiClient.post("/api/search/log/", {
    query: q,
    result_count: count,
    // Spread optional field only when it has a real value — never send `undefined`.
    ...(userIdentifier ? { user_identifier: userIdentifier } : {}),
  });
}

export async function logProductView(
  productId: number,
  opts?: { user_identifier?: string | null; session_id?: string | null }
): Promise<void> {
  await apiClient.post(`/api/products/${productId}/view/`, {
    ...(opts?.user_identifier ? { user_identifier: opts.user_identifier } : {}),
    ...(opts?.session_id      ? { session_id:      opts.session_id }      : {}),
  });
}

export async function logRecommendationClick(
  sourceProductId: number,
  recommendedProductId: number,
  userIdentifier?: string | null
): Promise<void> {
  await apiClient.post("/api/recommendations/click/", {
    source_product:     sourceProductId,
    recommended_product: recommendedProductId,
    ...(userIdentifier ? { user_identifier: userIdentifier } : {}),
  });
}
