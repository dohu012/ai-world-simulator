/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type CharacterId = string;
export type ContextSummary = string;
export type DecisionCorrelationId = string;
export type Id = string;
export type NonEmptyString = string;
export type Timestamp = string;
export type SchemaVersion = "1.0";
export type OracleRequestStatus =
  "pending" | "answered" | "expired" | "cancelled" | "resolved";
export type WorldId = string;

/**
 * An agent's request for player-provided information.
 */
export interface OracleRequest {
  agent_id: CharacterId;
  context_summary: ContextSummary;
  decision_correlation_id: DecisionCorrelationId;
  id: Id;
  question: NonEmptyString;
  real_deadline: Timestamp | null;
  requested_at: Timestamp;
  schema_version: SchemaVersion;
  status: OracleRequestStatus;
  world_deadline: Timestamp | null;
  world_id: WorldId;
}
