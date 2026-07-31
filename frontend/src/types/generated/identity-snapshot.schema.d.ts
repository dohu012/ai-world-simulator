/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type NonEmptyString = string;
export type Confidence = number;
export type ContentHash = string;
export type Timestamp = string;
export type Lifecycle = "active" | "superseded" | "reverted" | "invalidated";
export type PersonaSummary = string;
export type PolicyVersion = "evolution-policy-v1";
export type PreviousSnapshotId = string | null;
export type SchemaVersion = "1.0";
export type Version = number;

export interface IdentitySnapshot {
  agent_id: NonEmptyString;
  baseline_id: NonEmptyString;
  confidence: Confidence;
  content_hash: ContentHash;
  evidence_horizon: Timestamp;
  id: NonEmptyString;
  lifecycle?: Lifecycle;
  offsets?: Offsets;
  owner_id: NonEmptyString;
  persona_summary: PersonaSummary;
  policy_version?: PolicyVersion;
  previous_snapshot_id?: PreviousSnapshotId;
  schema_version: SchemaVersion;
  version: Version;
  world_id: NonEmptyString;
}
export interface Offsets {
  [k: string]: number;
}
