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
  retrieval_id?: string | null;
  retrieval_mode?: string | null;
  selected_memory_ids?: string[];
  memory_context_watermark?: string | null;
  memory_characters_used?: number | null;
  evolution_context_watermark?: string | null;
  identity_version?: number | null;
  relationship_versions?: Record<string, number>;
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
  evolution_context_watermark: string;
  identity_version: number;
  relationship_versions: Record<string, number>;
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

export interface EvolutionStateResponse {
  baseline: {
    id: string;
    generation: number;
    structured_state: Record<string, unknown>;
    persona_summary: string;
    content_hash: string;
  };
  identity: {
    id: string;
    version: number;
    offsets: Record<string, number>;
    confidence: number;
    persona_summary: string;
    evidence_horizon: string;
    content_hash: string;
  };
  relationships: Array<{
    id: string;
    target_type: "agent" | "oracle";
    target_id: string;
    version: number;
    dimensions: Record<string, number>;
    uncertainty: number;
    interpretation: string;
    evidence_horizon: string;
    content_hash: string;
  }>;
  changes: Array<{
    id: string;
    job_id: string;
    snapshot_kind: "identity" | "relationship";
    snapshot_id: string;
    dimension: string;
    proposed_magnitude: number;
    applied_magnitude: number;
    accepted: boolean;
    reason: string;
    rationale: string;
    evidence_memory_ids: string[];
    created_at: string;
  }>;
  context_watermark: string;
}

export interface ReflectionResponse {
  job_id: string;
  status: string;
  accepted_dimensions: number;
  rejected_dimensions: number;
  idempotent_replay: boolean;
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

export interface SevenDayScenarioResponse {
  version: string;
  current_day: number;
  status: string;
  residents: Array<Record<string, unknown>>;
  resources: Record<string, number>;
  capacities: Record<string, number>;
  events: Array<Record<string, unknown>>;
  plans: Array<{
    owner_id: string;
    objective: string;
    status: string;
    blockage_code: string | null;
  }>;
  actions: Array<{
    day: number;
    actor_id: string;
    action_type: string;
    status: string;
    consequence: string;
    failure_code: string | null;
  }>;
  outcomes: string[];
  model_calls: number;
}

export interface MemoryResponse {
  id: string;
  memory_type:
    "episodic" | "semantic" | "emotional" | "oracle" | "stage_summary";
  summary: string;
  occurred_at: string;
  importance: number;
  confidence: number;
  source_count: number;
  embedding_status: string;
  superseded: boolean;
}

export interface MemorySyncResponse {
  examined: number;
  admitted: number;
  rejected: number;
  deduplicated: number;
  jobs_created: number;
}

export interface MemoryEvaluationResponse {
  corpus_version: string;
  case_count: number;
  hybrid: {
    mode: string;
    metrics: MemoryEvaluationMetrics;
    failed_case_ids: string[];
  };
  fallback: {
    mode: string;
    metrics: MemoryEvaluationMetrics;
    failed_case_ids: string[];
  };
}

export interface MemoryEvaluationMetrics {
  case_count: number;
  required_recall_at_k: number;
  precision_at_k: number;
  mean_reciprocal_rank: number;
  forbidden_exposure_count: number;
  forbidden_exposure_rate: number;
  hard_gates_passed: boolean;
}

export interface MemoryRetrievalResponse {
  id: string;
  policy_version: string;
  mode: string;
  context_watermark: string;
  character_budget: number;
  characters_used: number;
  candidates: Array<{
    memory: MemoryResponse;
    rank: number;
    selected: boolean;
    exclusion_reason: string;
    scores: {
      lexical: number;
      semantic: number;
      recency: number;
      importance: number;
      goal: number;
      entity: number;
      location: number;
      emotion: number;
      contradiction: number;
      oracle: number;
      diversity_penalty: number;
      total: number;
    };
  }>;
}

export interface ReturnLoopResponse {
  summary: {
    id: string;
    source_watermark: string;
    claims: Array<{
      id: string;
      source_id: string;
      epistemic_class: string;
      text: string;
      visible_at: string;
    }>;
    narrative: string[];
  };
  inbox: Array<{ id: string; title: string; preview: string; read: boolean }>;
  preferences: {
    push_enabled: boolean;
    timezone: string;
    inbox_daily_cap: number;
    push_daily_cap: number;
  };
  debug: Record<string, string | number | boolean>;
}
