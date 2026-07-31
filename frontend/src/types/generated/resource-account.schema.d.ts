/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type Available = number;
export type Capacity = number | null;
export type Consumed = number;
export type NonEmptyString = string;
export type Reserved = number;
export type SchemaVersion = "1.0";
export type Version = number;

export interface ResourceAccount {
  available: Available;
  capacity?: Capacity;
  consumed: Consumed;
  holder_id: NonEmptyString;
  holder_kind: NonEmptyString;
  id: NonEmptyString;
  reserved: Reserved;
  resource_id: NonEmptyString;
  schema_version: SchemaVersion;
  version: Version;
  world_id: NonEmptyString;
}
