/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type CharacterId = string;
export type UnitFloat = number;
export type Id = string;
export type Timestamp = string;
export type JSONValue =
  | JSONPrimitive
  | JSONValue[]
  | {
      [k: string]: JSONValue;
    };
export type JSONPrimitive = string | number | boolean | null;
export type NonEmptyString = string;
export type SchemaVersion = "1.0";
export type SourceId = string | null;
export type BeliefSourceType =
  "observation" | "message" | "memory" | "inference" | "oracle" | "unknown";
export type WorldId = string;

/**
 * A fallible subjective proposition held by one agent.
 */
export interface AgentBelief {
  agent_id: CharacterId;
  confidence: UnitFloat;
  id: Id;
  last_updated_at: Timestamp;
  learned_at: Timestamp;
  object: JSONValue;
  predicate: NonEmptyString;
  schema_version: SchemaVersion;
  source_id: SourceId;
  source_type: BeliefSourceType;
  subject: NonEmptyString;
  world_id: WorldId;
}
