/** Shared aliases used by frontend domain consumers. */
export type JSONPrimitive = string | number | boolean | null;
export type JSONValue = JSONPrimitive | JSONValue[] | JSONObject;
export type JSONObject = { [key: string]: JSONValue };
export type SchemaVersion = "1.0";

export type WorldId = string;
export type CharacterId = string;
export type EventId = string;
export type FactId = string;
export type ObservationId = string;
export type ActionId = string;
