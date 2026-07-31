import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { SevenDayScenarioPanel } from "./seven-day-scenario-panel";

afterEach(() => vi.restoreAllMocks());

test("renders resource and plan state", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      text: async () =>
        JSON.stringify({
          version: "1.0.0",
          current_day: 5,
          status: "running",
          residents: [{ id: "char-chen-mo" }],
          resources: { food: 24, medicine: 6 },
          capacities: { rescue_seats: 10 },
          events: [],
          plans: [
            {
              owner_id: "char-chen-mo",
              objective: "Protect supplies",
              status: "blocked",
              blockage_code: "SHIPMENT_STOPPED",
            },
          ],
          actions: [],
          outcomes: [],
          model_calls: 0,
        }),
      headers: new Headers({ "content-type": "application/json" }),
    }),
  );
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  render(
    <QueryClientProvider client={client}>
      <SevenDayScenarioPanel />
    </QueryClientProvider>,
  );
  expect(await screen.findByText("Protect supplies")).toBeInTheDocument();
  expect(screen.getByText("SHIPMENT_STOPPED")).toBeInTheDocument();
  expect(screen.getByText("24")).toBeInTheDocument();
});
