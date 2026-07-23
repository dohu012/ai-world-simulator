/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type Timestamp = string;
export type Description = string;
export type WorldId = string;
export type NonEmptyString = string;
export type SchemaVersion = "1.0";
export type WorldStatus =
  "draft" | "running" | "paused" | "completed" | "archived";
export type PositiveFloat = number;
export type PositiveInt = number;

/**
 * Objective top-level metadata and clock for one simulated world.
 */
export interface World {
  created_at: Timestamp;
  current_time: Timestamp;
  description: Description;
  id: WorldId;
  name: NonEmptyString;
  schema_version: SchemaVersion;
  status: WorldStatus;
  time_scale: PositiveFloat;
  updated_at: Timestamp;
  version: PositiveInt;
}
