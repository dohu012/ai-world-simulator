import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, within } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { DemoAgentInputFeed } from "@/features/demo-world/demo-agent-input-feed";
import type { DemoAgentInputResponse } from "@/types/api";
import type { AgentProfile } from "@/types/domain";
import {
  demoCharacters,
  demoObservations,
  demoOracleResponse,
  demoWorld,
} from "./demo-world-data";

const demoAgentProfile: AgentProfile = {
  character_id: "char-chen-mo",
  persona_summary: "Chen Mo is a special demo agent with isolated local knowledge.",
  traits: { caution: 0.7, initiative: 0.6 },
  values: { safety: 0.9, truthfulness: 0.7 },
  desires: ["protect dependents", "understand local risk"],
  fears: ["acting on false information"],
  taboos: ["treat player revelation as a command"],
  abilities: ["observe", "wait", "speak"],
  decision_biases: { confirm_before_risk: 0.8 },
  oracle_relationship: { kind: "advice_only" },
  wake_policy: { mode: "fixed_demo" },
  schema_version: "1.0",
};

const demoInputResponse: DemoAgentInputResponse = {
  world: {
    id: demoWorld.id,
    name: demoWorld.name,
    current_time: demoWorld.current_time,
    schema_version: demoWorld.schema_version,
    version: demoWorld.version,
  },
  character: demoCharacters[2],
  agentProfile: demoAgentProfile,
  observations: [
    ...demoObservations.filter(
      (observation) => observation.agent_id === "char-chen-mo",
    ),
    {
      ...demoObservations[2],
      id: "obs-oracle-response-chen-north-gate",
      observation_type: "oracle",
      source_event_id: null,
      source_message_id: "oracle-response-chen-north-gate",
      received_messages: [
        {
          message_id: "oracle-response-chen-north-gate",
          sender_id: null,
          sent_at: demoOracleResponse.responded_at,
          content: demoOracleResponse.content,
        },
      ],
      metadata: {
        demo_projection: "oracle_response_as_observation",
      },
    },
  ],
};

function renderInputFeed(fetchImpl: typeof fetch) {
  vi.stubGlobal("fetch", fetchImpl);
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <DemoAgentInputFeed />
    </QueryClientProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

test("shows a loading state while requesting the current-agent input feed", () => {
  renderInputFeed(
    vi.fn(() => new Promise(() => undefined)) as unknown as typeof fetch,
  );

  expect(screen.getByLabelText("Agent Input Feed loading")).toBeInTheDocument();
});

test("renders the observation-only current-agent input feed", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => demoInputResponse,
  }) as unknown as typeof fetch;
  renderInputFeed(fetchMock);

  const feed = await screen.findByLabelText("Agent Input Feed");

  expect(within(feed).getByText("obs-chen-rumor")).toBeInTheDocument();
  expect(
    within(feed).getByText("obs-oracle-response-chen-north-gate"),
  ).toBeInTheDocument();
  expect(within(feed).getByText("oracle")).toBeInTheDocument();
  expect(within(feed).getByText(demoOracleResponse.content)).toBeInTheDocument();
  expect(within(feed).queryByText("ActionIntent")).not.toBeInTheDocument();
  expect(within(feed).queryByText("ActionResult")).not.toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledWith(
    expect.stringContaining("/demo/worlds/gray-harbor/me/input"),
    expect.objectContaining({
      headers: expect.objectContaining({ "X-Demo-Agent-Id": "char-chen-mo" }),
    }),
  );
});

test("shows the input feed error state", async () => {
  renderInputFeed(
    vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({
        error: {
          code: "DEMO_AGENT_FORBIDDEN",
          message: "blocked caller",
          details: null,
        },
      }),
    }) as unknown as typeof fetch,
  );

  expect(
    await screen.findByLabelText("Agent Input Feed error"),
  ).toHaveTextContent("blocked caller");
});
