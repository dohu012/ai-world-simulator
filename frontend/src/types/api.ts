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
  decision_ids?: string[];
}
export interface DecisionReplayItem {
  decision_id: string;
  agent_id: string;
  correlation_id: string;
  status: string;
  outcome: string | null;
  input_observation_watermark: string;
  final_action_intent_id: string | null;
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
  decisions?: DecisionReplayItem[];
}

export interface DecisionAttempt {
  attempt_number: number;
  provider: string;
  model: string;
  provider_request_id: string | null;
  failure_code: string | null;
  latency_ms: number;
  input_tokens: number | null;
  output_tokens: number | null;
  cost_usd: number | null;
}
export interface AgentDecisionResponse {
  decision_id: string;
  status: string;
  idempotent_replay: boolean;
  observation_watermark: string;
  observation_ids: string[];
  prompt_version: string;
  prompt_hash: string;
  schema_version: string;
  schema_hash: string;
  attempts: DecisionAttempt[];
  proposal: {
    action: "wait" | "move";
    affordance_id: string;
    rationale_summary: string;
    observation_ids: string[];
    observation_watermark: string;
  } | null;
  failure_code: string | null;
  action: {
    intent: ActionIntent;
    result: ActionResult;
    event: WorldEvent | null;
    idempotent_replay: boolean;
  } | null;
}

export interface RuntimeResponse {
  status: string;
  world_time: string;
  generation: number;
  version: number;
  next_due_world_time: string | null;
  backlog: number;
}

export interface OracleWindowResponse {
  request_id: string;
  agent_id: string;
  status: string;
  outcome: string | null;
  final_decision_id: string | null;
  question: string;
  context_summary: string;
  world_deadline: string;
  real_deadline: string;
}
