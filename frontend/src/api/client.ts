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
  const message =
    fromBody ?? error.message ?? "Request failed";
  return new ApiError(message, status, body);
}

const fromEnv = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "");
const baseURL =
  fromEnv || (import.meta.env.DEV ? "" : "http://127.0.0.1:8000");

export const apiClient = axios.create({
  baseURL,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
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
