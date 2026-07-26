import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, within } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { DemoAgentPreview } from "@/features/demo-world/demo-agent-preview";
import type { DemoAgentPerspectiveResponse, DemoWorldResponse } from "@/types/api";
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
} from "./demo-world-data";

const forbiddenObserverPayload: DemoWorldResponse = {
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

function renderPreview(fetchImpl: typeof fetch) {
  vi.stubGlobal("fetch", fetchImpl);
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <DemoAgentPreview />
    </QueryClientProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

test("shows a loading state while requesting the current-agent perspective", () => {
  renderPreview(
    vi.fn(() => new Promise(() => undefined)) as unknown as typeof fetch,
  );

  expect(screen.getByLabelText("Agent Preview loading")).toBeInTheDocument();
});

test("renders current-agent perspective from the me endpoint", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => demoPerspectiveResponse,
  }) as unknown as typeof fetch;
  renderPreview(fetchMock);

  const preview = await screen.findByLabelText("Agent Preview");

  expect(within(preview).getByText("char-chen-mo")).toBeInTheDocument();
  expect(within(preview).getByText(demoCharacters[2].name)).toBeInTheDocument();
  expect(
    within(preview).getByText(/只听到传言和街面变化/),
  ).toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledWith(
    expect.stringContaining("/demo/worlds/gray-harbor/me/perspective"),
    expect.objectContaining({
      headers: expect.objectContaining({ "X-Demo-Agent-Id": "char-chen-mo" }),
    }),
  );
});

test("shows the current-agent error state", async () => {
  renderPreview(
    vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({
        error: {
          code: "DEMO_AGENT_ID_REQUIRED",
          message: "missing caller",
          details: null,
        },
      }),
    }) as unknown as typeof fetch,
  );

  expect(await screen.findByLabelText("Agent Preview error")).toHaveTextContent(
    "missing caller",
  );
});

test("does not fall back to observer payload private records", async () => {
  renderPreview(
    vi.fn().mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/demo/worlds/gray-harbor")) {
        return Promise.resolve({
          ok: true,
          json: async () => forbiddenObserverPayload,
        });
      }
      return Promise.resolve({
        ok: true,
        json: async () => ({
          ...demoPerspectiveResponse,
          oracleRequests: [],
          oracleResponses: [],
          actionIntents: [],
          actionResults: [],
        }),
      });
    }) as unknown as typeof fetch,
  );

  const preview = await screen.findByLabelText("Agent Preview");

  expect(within(preview).getByText("No Oracle request.")).toBeInTheDocument();
  expect(within(preview).getByText("No action intent.")).toBeInTheDocument();
  expect(
    within(preview).queryByText(demoOracleRequest.question),
  ).not.toBeInTheDocument();
});
