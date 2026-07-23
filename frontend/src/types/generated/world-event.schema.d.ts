/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type CorrelationId = string;
export type Timestamp = string;
export type Description = string;
export type EventType =
  "state_changed" | "movement" | "speech" | "scheduled_event" | "system";
export type FactId = string;
export type FactIds = FactId[];
export type Id = string;
export type LocationId = string | null;
export type JSONValue =
  | JSONPrimitive
  | JSONValue[]
  | {
      [k: string]: JSONValue;
    };
export type JSONPrimitive = string | number | boolean | null;
export type CharacterId = string;
export type ParticipantIds = CharacterId[];
export type SchemaVersion = "1.0";
export type ActionId = string;
export type NonEmptyString = string;
export type FactVisibility = "public" | "restricted" | "secret" | "private";
export type WorldId = string;

/**
 * An occurrence that has happened in the objective world.
 */
export interface WorldEvent {
  correlation_id: CorrelationId;
  created_at: Timestamp;
  description: Description;
  event_type: EventType;
  fact_ids: FactIds;
  id: Id;
  location_id: LocationId;
  metadata: JSONObject;
  occurred_at: Timestamp;
  participant_ids: ParticipantIds;
  schema_version: SchemaVersion;
  source_action_id: ActionId | null;
  title: NonEmptyString;
  visibility: FactVisibility;
  world_id: WorldId;
}
export interface JSONObject {
  [k: string]: JSONValue;
}
