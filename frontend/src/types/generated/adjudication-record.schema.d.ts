/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type NonEmptyString = string;
export type Timestamp = string;
export type SchemaVersion = "1.0";
export type JSONValue =
  | JSONPrimitive
  | JSONValue[]
  | {
      [k: string]: JSONValue;
    };
export type JSONPrimitive = string | number | boolean | null;

export interface AdjudicationRecord {
  action_id: NonEmptyString;
  created_world_time: Timestamp;
  id: NonEmptyString;
  schema_version: SchemaVersion;
  trace: JSONObject;
  world_id: NonEmptyString;
}
export interface JSONObject {
  [k: string]: JSONValue;
}
