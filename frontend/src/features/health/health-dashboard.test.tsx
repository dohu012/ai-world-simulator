import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import Home from "@/app/page";

function renderHome() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <Home />
    </QueryClientProvider>,
  );
}

afterEach(() => vi.restoreAllMocks());

test("renders the home page and loading state", () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(
    () => new Promise(() => undefined),
  );
  renderHome();
  expect(screen.getByText("AI 世界观察与干预模拟器")).toBeInTheDocument();
  expect(screen.getAllByText("加载中")).toHaveLength(2);
});

test("shows healthy backend states", async () => {
  vi.spyOn(globalThis, "fetch")
    .mockResolvedValueOnce(
      new Response(JSON.stringify({ status: "ok" }), { status: 200 }),
    )
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          status: "ready",
          dependencies: { database: "ok", redis: "ok" },
        }),
        { status: 200 },
      ),
    );
  renderHome();
  await waitFor(() => expect(screen.getAllByText("正常")).toHaveLength(3));
});

test("shows failed request states", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(
      JSON.stringify({
        error: {
          code: "DEPENDENCY_UNAVAILABLE",
          message: "Unavailable",
          details: null,
        },
      }),
      { status: 503 },
    ),
  );
  renderHome();
  await waitFor(() => expect(screen.getAllByText("失败")).toHaveLength(2));
});
