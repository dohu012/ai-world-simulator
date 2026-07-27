import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { ReplayInspector } from "./replay-inspector";
import type { WorldReplayResponse } from "@/types/api";
import {
  demoActionIntent,
  demoActionResult,
  demoObservations,
  demoOracleRequest,
  demoOracleResponse,
  demoWorld,
  demoWorldEvents,
} from "./demo-world-data";

const chenEvent = demoWorldEvents.find(
  (event) => event.id === "event-chen-action-result",
)!;
const earlyEvent = demoWorldEvents[0];

const replay: WorldReplayResponse = {
  world_id: demoWorld.id,
  events: [chenEvent, earlyEvent],
  observations: [
    ...demoObservations.filter(
      (observation) => observation.source_event_id === earlyEvent.id,
    ),
    {
      ...demoObservations[0],
      id: "obs-chen-result-test",
      agent_id: "char-chen-mo",
      source_event_id: chenEvent.id,
    },
  ],
  oracle_requests: [demoOracleRequest],
  oracle_responses: [demoOracleResponse],
  action_intents: [demoActionIntent],
  action_results: [demoActionResult],
  chains: [
    {
      correlation_id: "corr-chen-oracle-decision",
      oracle_request_ids: [demoOracleRequest.id],
      oracle_response_ids: [demoOracleResponse.id],
      decision_ids: ["decision-chen-oracle-final"],
      action_intent_ids: [demoActionIntent.id],
      action_result_ids: [demoActionResult.id],
      event_ids: [chenEvent.id],
    },
  ],
};

function renderInspector() {
  const client = new QueryClient({
    defaultOptions: {
      queries: { retry: false, refetchOnWindowFocus: false },
    },
  });
  return render(
    <QueryClientProvider client={client}>
      <ReplayInspector />
    </QueryClientProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

test("shows loading state", () => {
  vi.stubGlobal(
    "fetch",
    vi.fn(() => new Promise(() => undefined)),
  );
  renderInspector();
  expect(screen.getByLabelText("Replay Inspector loading")).toBeInTheDocument();
});

test("shows typed API errors without retrying", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: false,
    status: 404,
    json: async () => ({
      error: {
        code: "DEMO_WORLD_NOT_SEEDED",
        message: "Gray Harbor has not been seeded.",
        details: {},
      },
    }),
  });
  vi.stubGlobal("fetch", fetchMock);
  renderInspector();
  expect(
    await screen.findByLabelText("Replay Inspector error"),
  ).toHaveTextContent("Gray Harbor has not been seeded.");
  expect(fetchMock).toHaveBeenCalledTimes(1);
});

test("shows empty replay state", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        ...replay,
        events: [],
        observations: [],
        chains: [],
      }),
    }),
  );
  renderInspector();
  expect(await screen.findByText("No replay events.")).toBeInTheDocument();
});

test("sorts events and renders source, counts, and Chen causal chain", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => replay,
  });
  vi.stubGlobal("fetch", fetchMock);
  renderInspector();

  const panel = await screen.findByLabelText("Replay Inspector");
  const rows = within(panel).getAllByRole("listitem");
  expect(rows[0]).toHaveTextContent(earlyEvent.title);
  expect(rows[1]).toHaveTextContent(chenEvent.title);
  expect(rows[1]).toHaveTextContent("intent-chen-contact-courier");
  expect(rows[1]).toHaveTextContent("1 linked");
  expect(panel).toHaveTextContent("corr-chen-oracle-decision");
  expect(panel).toHaveTextContent("1 decision");
  expect(panel).toHaveTextContent(
    "1 request · 1 response · 1 intent · 1 result · 1 event",
  );
  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/demo/worlds/gray-harbor/replay"),
      expect.any(Object),
    ),
  );
});
