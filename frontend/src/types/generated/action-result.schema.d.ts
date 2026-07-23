/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type ActionId = string;
export type CharacterId = string;
export type Timestamp = string;
export type CorrelationId = string;
export type FailureCode = string | null;
export type FailureReason = string | null;
export type EventId = string;
export type GeneratedEventIds = EventId[];
export type Id = string;
export type SchemaVersion = "1.0";
export type NonEmptyString = string;
export type JSONValue =
  | JSONPrimitive
  | JSONValue[]
  | {
      [k: string]: JSONValue;
    };
export type JSONPrimitive = string | number | boolean | null;
export type StateChanges = StateChange[];
export type ActionStatus =
  "accepted" | "succeeded" | "failed" | "rejected" | "cancelled";
export type WitnessCharacterIds = CharacterId[];
export type WorldId = string;

/**
 * The world adjudicator's outcome for an action intent.
 */
export interface ActionResult {
  action_id: ActionId;
  actor_id: CharacterId;
  completed_at: Timestamp | null;
  correlation_id: CorrelationId;
  failure_code: FailureCode;
  failure_reason: FailureReason;
  generated_event_ids: GeneratedEventIds;
  id: Id;
  schema_version: SchemaVersion;
  started_at: Timestamp;
  state_changes: StateChanges;
  status: ActionStatus;
  witness_character_ids: WitnessCharacterIds;
  world_id: WorldId;
}
/**
 * A single field-level change produced by world adjudication.
 */
export interface StateChange {
  entity_id: NonEmptyString;
  entity_type: NonEmptyString;
  field: NonEmptyString;
  new_value: JSONValue;
  old_value: JSONValue;
}
