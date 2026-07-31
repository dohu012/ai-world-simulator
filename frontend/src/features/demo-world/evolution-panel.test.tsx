import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { EvolutionPanel } from "./evolution-panel";

vi.mock("@/lib/api-client", () => ({
  apiGet: vi.fn().mockResolvedValue({
    baseline: {
      id: "baseline",
      generation: 1,
      structured_state: {},
      persona_summary: "Chen remains deliberate.",
      content_hash: "0".repeat(64),
    },
    identity: {
      id: "identity",
      version: 2,
      offsets: { caution: 0.04 },
      confidence: 0.7,
      persona_summary: "Chen is slightly more cautious.",
      evidence_horizon: "2026-07-28T00:00:00Z",
      content_hash: "1".repeat(64),
    },
    relationships: [
      {
        id: "oracle-edge",
        target_type: "oracle",
        target_id: "gray-harbor-oracle",
        version: 2,
        dimensions: { trust: -0.06, gratitude: 0.02 },
        uncertainty: 0.5,
        interpretation: "A lucky result did not validate poor advice.",
        evidence_horizon: "2026-07-28T00:00:00Z",
        content_hash: "2".repeat(64),
      },
    ],
    changes: [],
    context_watermark: "3".repeat(64),
  }),
  apiPost: vi.fn(),
}));

beforeEach(() => vi.clearAllMocks());

test("renders baseline, current version, and explicit relationship direction", async () => {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <EvolutionPanel />
    </QueryClientProvider>,
  );
  expect(await screen.findByText(/Immutable baseline/)).toBeInTheDocument();
  expect(
    screen.getByText(/Current derived identity · version 2/),
  ).toBeInTheDocument();
  expect(screen.getByText(/Chen → target/)).toBeInTheDocument();
  expect(screen.getByText(/lucky result/)).toBeInTheDocument();
});
