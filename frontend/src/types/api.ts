import type {
  ActionIntent,
  ActionResult,
  AgentBelief,
  AgentProfile,
  Character,
  Observation,
  OracleRequest,
  OracleResponse,
  World,
  WorldEvent,
} from "@/types/domain";

export interface HealthResponse {
  status: "ok";
}

export interface ReadinessResponse {
  status: "ready";
  dependencies: {
    database: "ok";
    redis: "ok";
  };
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: unknown;
  };
}

export interface DemoWorldResponse {
  world: World;
  characters: Character[];
  agentProfiles: AgentProfile[];
  events: WorldEvent[];
  observations: Observation[];
  beliefs: AgentBelief[];
  oracleRequests: OracleRequest[];
  oracleResponses: OracleResponse[];
  actionIntents: ActionIntent[];
  actionResults: ActionResult[];
}

export interface DemoAgentPerspectiveResponse {
  world: Pick<
    World,
    "id" | "name" | "current_time" | "schema_version" | "version"
  >;
  character: Character;
  agentProfile: AgentProfile;
  observations: Observation[];
  beliefs: AgentBelief[];
  oracleRequests: OracleRequest[];
  oracleResponses: OracleResponse[];
  actionIntents: ActionIntent[];
  actionResults: ActionResult[];
}

export interface DemoAgentInputResponse {
  world: Pick<
    World,
    "id" | "name" | "current_time" | "schema_version" | "version"
  >;
  character: Character;
  agentProfile: AgentProfile;
  observations: Observation[];
}

export interface ReplayChain {
  correlation_id: string;
  oracle_request_ids: string[];
  oracle_response_ids: string[];
  action_intent_ids: string[];
  action_result_ids: string[];
  event_ids: string[];
}

export interface WorldReplayResponse {
  world_id: string;
  events: WorldEvent[];
  observations: Observation[];
  oracle_requests: OracleRequest[];
  oracle_responses: OracleResponse[];
  action_intents: ActionIntent[];
  action_results: ActionResult[];
  chains: ReplayChain[];
}
