/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type NonNegativeInt = number;
export type Timestamp = string;
export type Description = string;
export type UnitFloat = number;
export type CharacterId = string;
export type IsSpecialAgent = boolean;
export type OptionalNonEmptyString = string;
export type NonEmptyString = string;
export type Occupation = string | null;
export type JSONValue =
  | JSONPrimitive
  | JSONValue[]
  | {
      [k: string]: JSONValue;
    };
export type JSONPrimitive = string | number | boolean | null;
export type SchemaVersion = "1.0";
export type CharacterStatus =
  "active" | "incapacitated" | "missing" | "dead" | "inactive";
export type PositiveInt = number;
export type WorldId = string;

/**
 * Objective character data; beliefs and private memories live elsewhere.
 */
export interface Character {
  age: NonNegativeInt | null;
  created_at: Timestamp;
  description: Description;
  health: UnitFloat;
  id: CharacterId;
  is_special_agent: IsSpecialAgent;
  location_id: OptionalNonEmptyString | null;
  name: NonEmptyString;
  occupation: Occupation;
  resources: JSONObject;
  schema_version: SchemaVersion;
  status: CharacterStatus;
  updated_at: Timestamp;
  version: PositiveInt;
  world_id: WorldId;
}
export interface JSONObject {
  [k: string]: JSONValue;
}
