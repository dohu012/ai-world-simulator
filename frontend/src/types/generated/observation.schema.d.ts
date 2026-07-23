/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type CharacterId = string;
export type ActionType = "move" | "speak" | "wait" | "custom";
export type NonEmptyString = string;
export type JSONValue =
  | JSONPrimitive
  | JSONValue[]
  | {
      [k: string]: JSONValue;
    };
export type JSONPrimitive = string | number | boolean | null;
export type AvailableActions = AvailableAction[];
export type UnitFloat = number;
export type FeltChanges = FeltChange[];
export type HeardStatements = HeardStatement[];
export type ObservationId = string;
export type ObservationType =
  "visual" | "auditory" | "message" | "oracle" | "mixed" | "internal";
export type Timestamp = string;
export type MessageId = string;
export type ReceivedMessages = ReceivedMessage[];
export type SchemaVersion = "1.0";
export type EventId = string;
export type SourceMessageId = string | null;
export type Description = string | null;
export type VisibleEntities = ObservedEntity[];
export type WorldId = string;

/**
 * Only the local information made available to a particular agent.
 */
export interface Observation {
  agent_id: CharacterId;
  available_actions: AvailableActions;
  felt_changes: FeltChanges;
  heard_statements: HeardStatements;
  id: ObservationId;
  metadata: JSONObject;
  observation_type: ObservationType;
  observed_at: Timestamp;
  received_messages: ReceivedMessages;
  schema_version: SchemaVersion;
  source_event_id: EventId | null;
  source_message_id: SourceMessageId;
  visible_entities: VisibleEntities;
  world_id: WorldId;
}
/**
 * An action affordance exposed to the agent, not an action result.
 */
export interface AvailableAction {
  action_type: ActionType;
  description: NonEmptyString;
  parameter_hints: JSONObject;
}
export interface JSONObject {
  [k: string]: JSONValue;
}
/**
 * A local, possibly imprecise sensation of change.
 */
export interface FeltChange {
  description: NonEmptyString;
  intensity: UnitFloat;
}
/**
 * A statement heard by the agent, without asserting its truth.
 */
export interface HeardStatement {
  content: NonEmptyString;
  speaker_id: CharacterId | null;
}
/**
 * A message delivered to the agent.
 */
export interface ReceivedMessage {
  content: NonEmptyString;
  message_id: MessageId;
  sender_id: CharacterId | null;
  sent_at: Timestamp;
}
/**
 * A partial entity view visible to the observing agent.
 */
export interface ObservedEntity {
  attributes: JSONObject;
  description: Description;
  entity: EntityReference;
  name: NonEmptyString;
}
/**
 * A lightweight reference to a domain entity.
 */
export interface EntityReference {
  entity_id: NonEmptyString;
  entity_type: NonEmptyString;
}
