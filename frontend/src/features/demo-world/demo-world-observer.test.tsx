import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { DemoWorldObserver } from "@/features/demo-world/demo-world-observer";
import {
  confidencePercent,
  getBeliefsForAgent,
  getObservationsForAgent,
} from "@/features/demo-world/demo-world-types";
import type {
  DemoAgentPerspectiveResponse,
  DemoWorldResponse,
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
} from "./demo-world-data";

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

const demoAgentProfiles: AgentProfile[] = demoCharacters.map((character) => ({
  character_id: character.id,
  persona_summary: `${character.name} is a special demo agent with isolated local knowledge.`,
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
}));

function perspectiveForAgent(agentId: string): DemoAgentPerspectiveResponse {
  const character = demoCharacters.find(
    (candidate) => candidate.id === agentId,
  );
  const agentProfile = demoAgentProfiles.find(
    (candidate) => candidate.character_id === agentId,
  );
  if (!character || !agentProfile) {
    throw new Error(`Unknown test agent: ${agentId}`);
  }

  const isChen = agentId === "char-chen-mo";
  return {
    world: {
      id: demoWorld.id,
      name: demoWorld.name,
      current_time: demoWorld.current_time,
      schema_version: demoWorld.schema_version,
      version: demoWorld.version,
    },
    character,
    agentProfile,
    observations: demoObservations.filter(
      (observation) => observation.agent_id === agentId,
    ),
    beliefs: demoBeliefs.filter((belief) => belief.agent_id === agentId),
    oracleRequests: isChen ? [demoOracleRequest] : [],
    oracleResponses: isChen ? [demoOracleResponse] : [],
    actionIntents: isChen ? [demoActionIntent] : [],
    actionResults: isChen ? [demoActionResult] : [],
  };
}

function renderObserver(fetchImpl: typeof fetch = successFetch()) {
  vi.stubGlobal("fetch", fetchImpl);
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, refetchOnWindowFocus: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <DemoWorldObserver />
    </QueryClientProvider>,
  );
}

function successFetch(payload: DemoWorldResponse = demoResponse) {
  return vi.fn().mockImplementation((input: RequestInfo | URL) => {
    const url = String(input);
    const perspectiveMatch = url.match(
      /\/demo\/worlds\/gray-harbor\/agents\/([^/]+)\/perspective$/,
    );
    const responseBody = perspectiveMatch
      ? perspectiveForAgent(perspectiveMatch[1])
      : payload;

    return Promise.resolve({
      ok: true,
      json: async () => responseBody,
    });
  }) as unknown as typeof fetch;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

test("shows a loading state while requesting the fixed world", () => {
  renderObserver(
    vi.fn(() => new Promise(() => undefined)) as unknown as typeof fetch,
  );

  expect(screen.getByLabelText("固定世界观察台加载中")).toBeInTheDocument();
});

test("shows a loading state while requesting the selected character perspective", async () => {
  renderObserver(
    vi.fn().mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/demo/worlds/gray-harbor")) {
        return Promise.resolve({
          ok: true,
          json: async () => demoResponse,
        });
      }
      return new Promise(() => undefined);
    }) as unknown as typeof fetch,
  );

  expect(
    await screen.findByLabelText("角色第一视角加载中"),
  ).toBeInTheDocument();
});

test("renders the API fixed world title and three special agents", async () => {
  renderObserver();

  expect(
    await screen.findByRole("heading", { name: "灰港封锁区" }),
  ).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /林知夏/ })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /周启明/ })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /陈沫/ })).toBeInTheDocument();
});

test("renders the selected character perspective success state", async () => {
  renderObserver();

  expect(
    await screen.findByRole("heading", { name: "陈沫的第一视角" }),
  ).toBeInTheDocument();
  expect(screen.getByText(/只听到传言和街面变化/)).toBeInTheDocument();
  const beliefs = screen
    .getByRole("heading", { name: "主观 Belief" })
    .closest("section");
  expect(beliefs).not.toBeNull();
  expect(
    within(beliefs as HTMLElement).getByText(/北门封锁/),
  ).toBeInTheDocument();
});

test("shows an error state when the demo API fails", async () => {
  renderObserver(
    vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({
        error: {
          code: "DEMO_DOWN",
          message: "fixture exploded",
          details: null,
        },
      }),
    }) as unknown as typeof fetch,
  );

  expect(await screen.findByText(/fixture exploded/)).toBeInTheDocument();
});

test("shows an error state when the selected character perspective API fails", async () => {
  renderObserver(
    vi.fn().mockImplementation((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/demo/worlds/gray-harbor")) {
        return Promise.resolve({
          ok: true,
          json: async () => demoResponse,
        });
      }
      return Promise.resolve({
        ok: false,
        status: 404,
        json: async () => ({
          error: {
            code: "DEMO_AGENT_NOT_FOUND",
            message: "agent vanished",
            details: null,
          },
        }),
      });
    }) as unknown as typeof fetch,
  );

  expect(await screen.findByText(/agent vanished/)).toBeInTheDocument();
});

test("separates objective world events from subjective observations", async () => {
  renderObserver();

  const objective = (
    await screen.findByRole("heading", { name: "客观世界事件时间线" })
  ).closest("section");
  const firstPerson = screen
    .getByRole("heading", { name: "陈沫的第一视角" })
    .closest("section");

  expect(objective).not.toBeNull();
  expect(firstPerson).not.toBeNull();
  expect(
    within(objective as HTMLElement).getByText("市政厅秘密批准北门封锁预案"),
  ).toBeInTheDocument();
  expect(
    within(firstPerson as HTMLElement).getByText(/只听到传言和街面变化/),
  ).toBeInTheDocument();
});

test("switches the selected character first-person view", async () => {
  const fetchMock = successFetch();
  renderObserver(fetchMock);

  fireEvent.click(await screen.findByRole("button", { name: /林知夏/ }));

  expect(
    await screen.findByRole("heading", { name: "林知夏的第一视角" }),
  ).toBeInTheDocument();
  expect(await screen.findByText(/不知道北门封锁预案/)).toBeInTheDocument();
  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(
        "/demo/worlds/gray-harbor/agents/char-lin-zhixia/perspective",
      ),
      expect.any(Object),
    ),
  );
});

test("does not render another character's mocked perspective data", async () => {
  renderObserver();

  const firstPerson = (
    await screen.findByRole("heading", { name: "陈沫的第一视角" })
  ).closest("section");

  expect(firstPerson).not.toBeNull();
  expect(
    within(firstPerson as HTMLElement).getByText(/只听到传言和街面变化/),
  ).toBeInTheDocument();
  expect(
    within(firstPerson as HTMLElement).queryByText(/不知道北门封锁预案/),
  ).not.toBeInTheDocument();
});

test("shows revelation request and advice rather than a command", async () => {
  renderObserver();

  expect(await screen.findByText("玩家启示请求")).toBeInTheDocument();
  expect(screen.getByText(/建议是信息，不是命令/)).toBeInTheDocument();
  expect(screen.queryByText(/命令角色执行/)).not.toBeInTheDocument();
  expect(screen.queryByText(/强制改变决定/)).not.toBeInTheDocument();
});

test("hides Chen Mo's oracle request from Lin Zhixia's perspective", async () => {
  renderObserver();

  fireEvent.click(await screen.findByRole("button", { name: /林知夏/ }));

  expect(
    await screen.findByText("当前角色暂无玩家启示请求。"),
  ).toBeInTheDocument();
  expect(
    screen.queryByText(/是否应该带孩子连夜前往北门/),
  ).not.toBeInTheDocument();
});

test("renders action intent and adjudicated result distinctly", async () => {
  renderObserver();

  expect(await screen.findByText("ActionIntent")).toBeInTheDocument();
  expect(screen.getByText(/只表示角色想尝试/)).toBeInTheDocument();
  expect(screen.getByText("ActionResult")).toBeInTheDocument();
  expect(screen.getByText(/由世界裁定产生/)).toBeInTheDocument();
});

test("filters observations and beliefs by agent with pure helpers", () => {
  expect(
    getObservationsForAgent(demoObservations, "char-chen-mo"),
  ).toHaveLength(1);
  const beliefs = getBeliefsForAgent(demoBeliefs, "char-chen-mo");
  expect(beliefs).toHaveLength(1);
  expect(confidencePercent(beliefs[0])).toBe("42%");
});
