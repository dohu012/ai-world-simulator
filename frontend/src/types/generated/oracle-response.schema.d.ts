/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type CharacterId = string;
export type UnitFloat = number;
export type NonEmptyString = string;
export type Id = string;
export type RequestId = string;
export type Timestamp = string;
export type SchemaVersion = "1.0";
export type WorldId = string;

/**
 * Player-provided information that may later become an observation.
 */
export interface OracleResponse {
  agent_id: CharacterId;
  clarity: UnitFloat;
  content: NonEmptyString;
  id: Id;
  request_id: RequestId;
  responded_at: Timestamp;
  schema_version: SchemaVersion;
  world_id: WorldId;
}
