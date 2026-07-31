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
export type Priority = number;
export type SchemaVersion = "1.0";
export type Version = number;

export interface AgentGoal {
  failure_predicate: JSONObject;
  horizon_world_time: Timestamp;
  id: NonEmptyString;
  objective_type: NonEmptyString;
  owner_id: NonEmptyString;
  priority: Priority;
  privacy_class: NonEmptyString;
  schema_version: SchemaVersion;
  status: NonEmptyString;
  success_predicate: JSONObject;
  version: Version;
  world_id: NonEmptyString;
}
export interface JSONObject {
  [k: string]: JSONValue;
}
