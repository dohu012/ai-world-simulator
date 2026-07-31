/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type JSONValue =
  | JSONPrimitive
  | JSONValue[]
  | {
      [k: string]: JSONValue;
    };
export type JSONPrimitive = string | number | boolean | null;
export type Timestamp = string;
export type NonEmptyString = string;
export type OneShot = boolean;
export type PolicyVersion = number;
export type SchemaVersion = "1.0";

export interface ConditionalWorldEvent {
  condition: JSONObject;
  deadline_world_time: Timestamp;
  event_specification: JSONObject;
  id: NonEmptyString;
  idempotency_key: NonEmptyString;
  one_shot?: OneShot;
  policy_version: PolicyVersion;
  schema_version: SchemaVersion;
  status: NonEmptyString;
  world_id: NonEmptyString;
}
export interface JSONObject {
  [k: string]: JSONValue;
}
