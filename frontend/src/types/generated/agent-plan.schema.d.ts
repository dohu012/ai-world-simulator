/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type BlockageCode = string | null;
export type CurrentStep = number;
export type Timestamp = string;
export type FencingToken = number;
export type NonEmptyString = string;
export type ReplanCount = number;
export type RetryCount = number;
export type SchemaVersion = "1.0";
export type PlanStatus =
  | "draft"
  | "active"
  | "waiting"
  | "blocked"
  | "abandoned"
  | "failed"
  | "completed"
  | "cancelled";
export type StepCount = number;
export type Version = number;

export interface AgentPlan {
  blockage_code: BlockageCode;
  current_step: CurrentStep;
  deadline_world_time: Timestamp;
  fencing_token: FencingToken;
  goal_id: NonEmptyString;
  id: NonEmptyString;
  owner_id: NonEmptyString;
  replan_count: ReplanCount;
  retry_count: RetryCount;
  schema_version: SchemaVersion;
  slot: NonEmptyString;
  status: PlanStatus;
  step_count: StepCount;
  version: Version;
  world_id: NonEmptyString;
}
