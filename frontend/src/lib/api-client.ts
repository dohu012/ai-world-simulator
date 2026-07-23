import type { ApiErrorBody } from "@/types/api";

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

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

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: { Accept: "application/json" },
  });
  const body: unknown = await response.json();

  if (!response.ok) {
    const errorBody = body as Partial<ApiErrorBody>;
    throw new ApiClientError(
      errorBody.error?.message ?? "API request failed",
      response.status,
      errorBody.error?.code ?? "UNKNOWN_ERROR",
      errorBody.error?.details ?? null,
    );
  }
  return body as T;
}
