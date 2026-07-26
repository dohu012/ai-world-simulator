import { afterEach, describe, expect, test, vi } from "vitest";

import { apiGet } from "./api-client";

afterEach(() => vi.unstubAllGlobals());

describe("apiGet response parsing", () => {
  test("preserves typed JSON API errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({
      error: { code: "DATABASE_UNAVAILABLE", message: "Database unavailable.", details: null },
    }), { status: 503, headers: { "content-type": "application/json" } })));
    await expect(apiGet("/demo")).rejects.toMatchObject({
      status: 503, code: "DATABASE_UNAVAILABLE", message: "Database unavailable.",
    });
  });

  test("turns a plain-text 500 into a stable client error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      new Response("Internal Server Error", { status: 500 }),
    ));
    await expect(apiGet("/demo")).rejects.toEqual(
      expect.objectContaining({
        status: 500, code: "HTTP_ERROR",
        message: "Backend service is temporarily unavailable.",
      }),
    );
  });
});

