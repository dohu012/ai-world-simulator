import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import Home from "@/app/page";
import type {
  DemoAgentInputResponse,
  DemoAgentPerspectiveResponse,
  DemoWorldResponse,
  WorldReplayResponse,
} from "@/types/api";
import type { AgentProfile } from "@/types/domain";
import {
  demoActionIntent,
  demoActionResult,
  demoBeliefs,
  demoCharacters,
  demoObservations,
  demoOracleRequest,
  demoOracleResponse,
  demoWorld,
  demoWorldEvents,
} from "../demo-world/demo-world-data";

const demoResponse: DemoWorldResponse = {
  world: demoWorld,
  characters: demoCharacters,
  agentProfiles: [],
  events: demoWorldEvents,
  observations: demoObservations,
  beliefs: demoBeliefs,
  oracleRequests: [demoOracleRequest],
  oracleResponses: [demoOracleResponse],
  actionIntents: [demoActionIntent],
  actionResults: [demoActionResult],
};

const demoReplayResponse: WorldReplayResponse = {
  world_id: demoWorld.id,
  events: demoWorldEvents,
  observations: demoObservations,
  oracle_requests: [demoOracleRequest],
  oracle_responses: [demoOracleResponse],
  action_intents: [demoActionIntent],
  action_results: [demoActionResult],
  chains: [],
};

const demoAgentProfile: AgentProfile = {
  character_id: "char-chen-mo",
  persona_summary:
    "陈沫 is a special demo agent with isolated local knowledge.",
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

const demoPerspectiveResponse: DemoAgentPerspectiveResponse = {
  world: {
    id: demoWorld.id,
    name: demoWorld.name,
    current_time: demoWorld.current_time,
    schema_version: demoWorld.schema_version,
    version: demoWorld.version,
  },
  character: demoCharacters[2],
  agentProfile: demoAgentProfile,
  observations: demoObservations.filter(
    (observation) => observation.agent_id === "char-chen-mo",
  ),
  beliefs: demoBeliefs.filter((belief) => belief.agent_id === "char-chen-mo"),
  oracleRequests: [demoOracleRequest],
  oracleResponses: [demoOracleResponse],
  actionIntents: [demoActionIntent],
  actionResults: [demoActionResult],
};

const demoInputResponse: DemoAgentInputResponse = {
  world: demoPerspectiveResponse.world,
  character: demoPerspectiveResponse.character,
  agentProfile: demoPerspectiveResponse.agentProfile,
  observations: [
    ...demoPerspectiveResponse.observations,
    {
      ...demoPerspectiveResponse.observations[0],
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

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status });
}

afterEach(() => vi.restoreAllMocks());

test("renders the home page and loading state", () => {
  vi.spyOn(globalThis, "fetch").mockImplementation(
    () => new Promise(() => undefined),
  );
  renderHome();
  expect(screen.getByLabelText("固定世界观察台加载中")).toBeInTheDocument();
  expect(screen.getAllByText("加载中")).toHaveLength(2);
});

test("shows healthy backend states", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
    const url = String(input);
    if (url.endsWith("/demo/worlds/gray-harbor")) {
      return Promise.resolve(jsonResponse(demoResponse));
    }
    if (
      url.endsWith("/demo/worlds/gray-harbor/agents/char-chen-mo/perspective")
    ) {
      return Promise.resolve(jsonResponse(demoPerspectiveResponse));
    }
    if (url.endsWith("/demo/worlds/gray-harbor/me/perspective")) {
      return Promise.resolve(jsonResponse(demoPerspectiveResponse));
    }
    if (url.endsWith("/demo/worlds/gray-harbor/me/input")) {
      return Promise.resolve(jsonResponse(demoInputResponse));
    }
    if (url.endsWith("/demo/worlds/gray-harbor/replay")) {
      return Promise.resolve(jsonResponse(demoReplayResponse));
    }
    if (url.endsWith("/health/ready")) {
      return Promise.resolve(
        jsonResponse({
          status: "ready",
          dependencies: { database: "ok", redis: "ok" },
        }),
      );
    }
    return Promise.resolve(jsonResponse({ status: "ok" }));
  });
  renderHome();
  expect(
    await screen.findByRole("heading", { name: "灰港封锁区" }),
  ).toBeInTheDocument();
  await waitFor(() => expect(screen.getAllByText("正常")).toHaveLength(3));
});

test("shows failed request states", async () => {
  vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
    const url = String(input);
    if (url.endsWith("/demo/worlds/gray-harbor")) {
      return Promise.resolve(jsonResponse(demoResponse));
    }
    if (url.endsWith("/demo/worlds/gray-harbor/me/perspective")) {
      return Promise.resolve(jsonResponse(demoPerspectiveResponse));
    }
    if (url.endsWith("/demo/worlds/gray-harbor/me/input")) {
      return Promise.resolve(jsonResponse(demoInputResponse));
    }
    return Promise.resolve(
      jsonResponse(
        {
          error: {
            code: "DEPENDENCY_UNAVAILABLE",
            message: "Unavailable",
            details: null,
          },
        },
        503,
      ),
    );
  });
  renderHome();
  await waitFor(() => expect(screen.getAllByText("失败")).toHaveLength(2));
});
