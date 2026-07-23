/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type ActionType = "move" | "speak" | "wait" | "custom";
export type CharacterId = string;
export type CorrelationId = string;
export type NonNegativeFloat = number;
export type ActionId = string;
export type JSONValue =
  | JSONPrimitive
  | JSONValue[]
  | {
      [k: string]: JSONValue;
    };
export type JSONPrimitive = string | number | boolean | null;
export type NonEmptyString = string;
export type SchemaVersion = "1.0";
export type Timestamp = string;
export type WorldId = string;

/**
 * An agent's request to attempt an action; it makes no success claim.
 */
export interface ActionIntent {
  action_type: ActionType;
  actor_id: CharacterId;
  correlation_id: CorrelationId;
  expected_duration: NonNegativeFloat | null;
  id: ActionId;
  parameters: JSONObject;
  reason_summary: NonEmptyString;
  schema_version: SchemaVersion;
  submitted_at: Timestamp;
  world_id: WorldId;
}
export interface JSONObject {
  [k: string]: JSONValue;
}
