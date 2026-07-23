/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type Timestamp = string;
export type FactId = string;
export type JSONValue =
  | JSONPrimitive
  | JSONValue[]
  | {
      [k: string]: JSONValue;
    };
export type JSONPrimitive = string | number | boolean | null;
export type NonEmptyString = string;
export type SchemaVersion = "1.0";
export type EventId = string;
export type PositiveInt = number;
export type FactVisibility = "public" | "restricted" | "secret" | "private";
export type WorldId = string;

/**
 * An objective proposition in world state, independent of any agent belief.
 */
export interface WorldFact {
  created_at: Timestamp;
  id: FactId;
  object: JSONValue;
  predicate: NonEmptyString;
  schema_version: SchemaVersion;
  source_event_id: EventId | null;
  subject: NonEmptyString;
  valid_from: Timestamp;
  valid_until: Timestamp | null;
  version: PositiveInt;
  visibility: FactVisibility;
  world_id: WorldId;
}
