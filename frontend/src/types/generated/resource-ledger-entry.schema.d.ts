/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type Amount = number;
export type FromAccountId = string | null;
export type NonEmptyString = string;
export type SchemaVersion = "1.0";
export type SourceActionId = string | null;
export type SourceEventId = string | null;
export type ToAccountId = string | null;
export type Timestamp = string;

export interface ResourceLedgerEntry {
  amount: Amount;
  from_account_id: FromAccountId;
  id: NonEmptyString;
  idempotency_key: NonEmptyString;
  operation: NonEmptyString;
  reason_code: NonEmptyString;
  resource_id: NonEmptyString;
  schema_version: SchemaVersion;
  source_action_id: SourceActionId;
  source_event_id: SourceEventId;
  to_account_id: ToAccountId;
  unit: NonEmptyString;
  world_id: NonEmptyString;
  world_time: Timestamp;
}
