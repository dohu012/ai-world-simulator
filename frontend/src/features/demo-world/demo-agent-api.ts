import { apiGet, apiPost } from "@/lib/api-client";
import type {
  DemoAgentInputResponse,
  DemoAgentPerspectiveResponse,
  AgentDecisionResponse,
} from "@/types/api";

export const demoCurrentAgentId = "char-chen-mo";

export function getGrayHarborCurrentAgentPerspective() {
  return apiGet<DemoAgentPerspectiveResponse>(
    "/demo/worlds/gray-harbor/me/perspective",
    {
      headers: { "X-Demo-Agent-Id": demoCurrentAgentId },
    },
  );
}

export function getGrayHarborCurrentAgentInput() {
  return apiGet<DemoAgentInputResponse>("/demo/worlds/gray-harbor/me/input", {
    headers: { "X-Demo-Agent-Id": demoCurrentAgentId },
  });
}

export function decideGrayHarborOnce(idempotencyKey: string) {
  return apiPost<AgentDecisionResponse>(
    "/demo/worlds/gray-harbor/me/decisions",
    { idempotency_key: idempotencyKey },
    { headers: { "X-Demo-Agent-Id": demoCurrentAgentId } },
  );
}
