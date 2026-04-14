import axios, { AxiosError, isAxiosError } from "axios";

/**
 * Structured API failure with optional HTTP status (e.g. 404) and raw response body.
 */
export class ApiError extends Error {
  readonly status: number | undefined;
  readonly body: unknown;

  constructor(message: string, status: number | undefined, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

function messageFromDrfBody(data: unknown): string | null {
  if (!data || typeof data !== "object") {
    return null;
  }
  const record = data as Record<string, unknown>;
  if (typeof record.detail === "string") {
    return record.detail;
  }
  const firstKey = Object.keys(record)[0];
  if (!firstKey) {
    return null;
  }
  const val = record[firstKey];
  if (Array.isArray(val) && val.length > 0) {
    return String(val[0]);
  }
  if (typeof val === "string") {
    return val;
  }
  return null;
}

function normalizeAxiosError(error: AxiosError): ApiError {
  const status = error.response?.status;
  const body = error.response?.data;
  const fromBody = body ? messageFromDrfBody(body) : null;
  const message = fromBody ?? error.message ?? "Request failed";
  return new ApiError(message, status, body);
}

// In dev, Vite proxies /api/* → localhost:8000, so baseURL stays "".
// In production, VITE_API_BASE_URL is baked in from frontend/.env.production.
const baseURL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export const apiClient = axios.create({
  baseURL,
  // Only Accept — NOT Content-Type.
  // Setting Content-Type as a default triggers a CORS preflight OPTIONS request
  // for every GET (because application/json is a non-simple header per the CORS spec).
  // Axios sets Content-Type automatically when a request body is present (POST/PUT/PATCH).
  headers: {
    Accept: "application/json",
  },
  timeout: 30_000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (isAxiosError(error)) {
      return Promise.reject(normalizeAxiosError(error));
    }
    return Promise.reject(
      error instanceof Error ? error : new Error(String(error))
    );
  }
);

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}
