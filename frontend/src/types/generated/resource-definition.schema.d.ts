/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type NonEmptyString = string;
export type Divisible = boolean;
export type SchemaVersion = "1.0";
export type Version = number;

export interface ResourceDefinition {
  conservation_policy: NonEmptyString;
  divisible?: Divisible;
  id: NonEmptyString;
  privacy_class: NonEmptyString;
  resource_type: NonEmptyString;
  schema_version: SchemaVersion;
  unit: NonEmptyString;
  version: Version;
  world_id: NonEmptyString;
}
