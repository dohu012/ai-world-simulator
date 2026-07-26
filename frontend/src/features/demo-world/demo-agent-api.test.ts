import { afterEach, expect, test, vi } from "vitest";

import {
  demoCurrentAgentId,
  getGrayHarborCurrentAgentInput,
  getGrayHarborCurrentAgentPerspective,
} from "@/features/demo-world/demo-agent-api";
import type {
  DemoAgentInputResponse,
  DemoAgentPerspectiveResponse,
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

afterEach(() => {
  vi.unstubAllGlobals();
});

test("requests the current-agent perspective with the fixed demo caller header", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => demoPerspectiveResponse,
  }) as unknown as typeof fetch;
  vi.stubGlobal("fetch", fetchMock);

  const response = await getGrayHarborCurrentAgentPerspective();

  expect(response.character.id).toBe("char-chen-mo");
  expect(fetchMock).toHaveBeenCalledWith(
    expect.stringContaining("/demo/worlds/gray-harbor/me/perspective"),
    expect.objectContaining({
      headers: expect.objectContaining({
        Accept: "application/json",
        "X-Demo-Agent-Id": demoCurrentAgentId,
      }),
    }),
  );
});

test("surfaces current-agent perspective API errors without observer data fallback", async () => {
  vi.stubGlobal(
    "fetch",
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
    }),
  );

  await expect(getGrayHarborCurrentAgentPerspective()).rejects.toMatchObject({
    status: 401,
    code: "DEMO_AGENT_ID_REQUIRED",
    message: "missing caller",
  });
});

test("requests the current-agent input feed with the fixed demo caller header", async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => demoInputResponse,
  }) as unknown as typeof fetch;
  vi.stubGlobal("fetch", fetchMock);

  const response = await getGrayHarborCurrentAgentInput();

  expect(response.observations.map((observation) => observation.id)).toContain(
    "obs-oracle-response-chen-north-gate",
  );
  expect(fetchMock).toHaveBeenCalledWith(
    expect.stringContaining("/demo/worlds/gray-harbor/me/input"),
    expect.objectContaining({
      headers: expect.objectContaining({
        Accept: "application/json",
        "X-Demo-Agent-Id": demoCurrentAgentId,
      }),
    }),
  );
});

test("surfaces current-agent input feed API errors", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({
        error: {
          code: "DEMO_AGENT_FORBIDDEN",
          message: "unknown caller",
          details: null,
        },
      }),
    }),
  );

  await expect(getGrayHarborCurrentAgentInput()).rejects.toMatchObject({
    status: 403,
    code: "DEMO_AGENT_FORBIDDEN",
    message: "unknown caller",
  });
});
