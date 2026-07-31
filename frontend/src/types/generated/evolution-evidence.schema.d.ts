/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type NonEmptyString = string;
export type Timestamp = string;
export type EvidenceRole =
  | "direct_interaction"
  | "reported_interaction"
  | "outcome"
  | "repeated_pattern"
  | "contradiction"
  | "reflection"
  | "oracle_event";
export type SchemaVersion = "1.0";
export type SourceType = "observation" | "memory" | "action_result";
export type Summary = string;

export interface EvolutionEvidence {
  agent_id: NonEmptyString;
  id: NonEmptyString;
  independent_key: NonEmptyString;
  occurred_at: Timestamp;
  owner_id: NonEmptyString;
  role: EvidenceRole;
  schema_version: SchemaVersion;
  source_id: NonEmptyString;
  source_type: SourceType;
  summary: Summary;
  visible_from: Timestamp;
  world_id: NonEmptyString;
}
