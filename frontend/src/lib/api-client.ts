import type { ApiErrorBody } from "@/types/api";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code: string,
    public readonly details: unknown,
  ) {
    super(message);
  }
}

interface ApiGetOptions {
  headers?: HeadersInit;
}

async function readResponseBody(response: Response): Promise<unknown> {
  // Some test/service-worker response doubles expose json() without text().
  if (typeof response.text !== "function") return response.json();
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    if (!response.ok) return text;
    throw new ApiClientError(
      "API returned an invalid response.",
      response.status,
      "INVALID_API_RESPONSE",
      { contentType: response.headers.get("content-type") },
    );
  }
}

export async function apiGet<T>(
  path: string,
  options: ApiGetOptions = {},
): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: { Accept: "application/json", ...options.headers },
  });
  const body = await readResponseBody(response);

  if (!response.ok) {
    const errorBody =
      typeof body === "object" && body !== null
        ? (body as Partial<ApiErrorBody>)
        : undefined;
    throw new ApiClientError(
      errorBody?.error?.message ??
        (response.status >= 500
          ? "Backend service is temporarily unavailable."
          : "API request failed."),
      response.status,
      errorBody?.error?.code ?? "HTTP_ERROR",
      errorBody?.error?.details ?? null,
    );
  }
  return body as T;
}

export async function apiPost<T>(
  path: string,
  body: unknown,
  options: ApiGetOptions = {},
): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...options.headers,
    },
    body: JSON.stringify(body),
  });
  const value = await readResponseBody(response);
  if (!response.ok) {
    const errorBody =
      typeof value === "object" && value !== null
        ? (value as Partial<ApiErrorBody>)
        : undefined;
    throw new ApiClientError(
      errorBody?.error?.message ?? "API request failed.",
      response.status,
      errorBody?.error?.code ?? "HTTP_ERROR",
      errorBody?.error?.details ?? null,
    );
  }
  return value as T;
}

export async function apiDelete(
  path: string,
  options: ApiGetOptions = {},
): Promise<void> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: "DELETE",
    headers: { Accept: "application/json", ...options.headers },
  });
  if (!response.ok) {
    throw new ApiClientError(
      "API request failed.",
      response.status,
      "HTTP_ERROR",
      null,
    );
  }
}
