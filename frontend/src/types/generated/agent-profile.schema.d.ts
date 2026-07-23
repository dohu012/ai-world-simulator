/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type Abilities = string[];
export type CharacterId = string;
export type UnitFloat = number;
export type Desires = string[];
export type Fears = string[];
export type JSONValue =
  | JSONPrimitive
  | JSONValue[]
  | {
      [k: string]: JSONValue;
    };
export type JSONPrimitive = string | number | boolean | null;
export type NonEmptyString = string;
export type SchemaVersion = "1.0";
export type Taboos = string[];

/**
 * Stable decision configuration for a special character.
 */
export interface AgentProfile {
  abilities: Abilities;
  character_id: CharacterId;
  decision_biases: DecisionBiases;
  desires: Desires;
  fears: Fears;
  oracle_relationship: JSONObject;
  persona_summary: NonEmptyString;
  schema_version: SchemaVersion;
  taboos: Taboos;
  traits: Traits;
  values: Values;
  wake_policy: JSONObject;
}
export interface DecisionBiases {
  [k: string]: UnitFloat;
}
export interface JSONObject {
  [k: string]: JSONValue;
}
export interface Traits {
  [k: string]: UnitFloat;
}
export interface Values {
  [k: string]: UnitFloat;
}
