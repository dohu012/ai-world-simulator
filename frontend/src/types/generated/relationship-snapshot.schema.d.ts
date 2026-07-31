/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type ContentHash = string;
export type Timestamp = string;
export type NonEmptyString = string;
export type Interpretation = string;
export type PolicyVersion = "evolution-policy-v1";
export type PreviousSnapshotId = string | null;
export type SchemaVersion = "1.0";
export type TargetType = "agent" | "oracle";
export type Uncertainty = number;
export type Version = number;

export interface RelationshipSnapshot {
  content_hash: ContentHash;
  dimensions?: Dimensions;
  evidence_horizon: Timestamp;
  id: NonEmptyString;
  interpretation: Interpretation;
  owner_id: NonEmptyString;
  policy_version?: PolicyVersion;
  previous_snapshot_id?: PreviousSnapshotId;
  schema_version: SchemaVersion;
  subject_agent_id: NonEmptyString;
  target_id: NonEmptyString;
  target_type: TargetType;
  uncertainty: Uncertainty;
  version: Version;
  world_id: NonEmptyString;
}
export interface Dimensions {
  [k: string]: number;
}
