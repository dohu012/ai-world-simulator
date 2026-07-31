/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type UnitFloat = number;
export type AdviceObservationId = string | null;
export type ChosenActionId = string | null;
/**
 * @maxItems 8
 */
export type EmotionLabels =
  | []
  | [NonEmptyString]
  | [NonEmptyString, NonEmptyString]
  | [NonEmptyString, NonEmptyString, NonEmptyString]
  | [NonEmptyString, NonEmptyString, NonEmptyString, NonEmptyString]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ];
export type NonEmptyString = string;
export type Timestamp = string;
export type EpistemicStatus = "observed" | "subjective" | "inferred";
/**
 * @maxItems 16
 */
export type GoalIds =
  | []
  | [NonEmptyString]
  | [NonEmptyString, NonEmptyString]
  | [NonEmptyString, NonEmptyString, NonEmptyString]
  | [NonEmptyString, NonEmptyString, NonEmptyString, NonEmptyString]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ];
export type Interpretation = string;
/**
 * @maxItems 32
 */
export type InvolvedEntityIds = NonEmptyString[];
/**
 * @maxItems 16
 */
export type LocationIds =
  | []
  | [NonEmptyString]
  | [NonEmptyString, NonEmptyString]
  | [NonEmptyString, NonEmptyString, NonEmptyString]
  | [NonEmptyString, NonEmptyString, NonEmptyString, NonEmptyString]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ];
export type MemoryType = "oracle";
export type ModelRevision = string | null;
export type OutcomeEventId = string | null;
export type OutcomeSummary = string | null;
/**
 * @maxItems 16
 */
export type PlanIds =
  | []
  | [NonEmptyString]
  | [NonEmptyString, NonEmptyString]
  | [NonEmptyString, NonEmptyString, NonEmptyString]
  | [NonEmptyString, NonEmptyString, NonEmptyString, NonEmptyString]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ]
  | [
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
      NonEmptyString,
    ];
export type SchemaVersion = "1.0";
export type SilenceReason = string | null;
/**
 * @minItems 1
 * @maxItems 32
 */
export type Sources = [SourceReference, ...SourceReference[]];
export type SourceType =
  | "observation"
  | "event"
  | "action"
  | "action_result"
  | "message"
  | "oracle"
  | "belief"
  | "plan"
  | "memory";
export type Summary = string;
export type SupersedesId = string | null;
export type Version = number;

export interface OracleMemory {
  admission_score: UnitFloat;
  advice_observation_id: AdviceObservationId;
  chosen_action_id: ChosenActionId;
  confidence: UnitFloat;
  emotion_intensity?: number;
  emotion_labels?: EmotionLabels;
  ended_at?: Timestamp | null;
  epistemic_status: EpistemicStatus;
  goal_ids?: GoalIds;
  id: NonEmptyString;
  importance_features: ImportanceFeatures;
  interpretation: Interpretation;
  involved_entity_ids?: InvolvedEntityIds;
  location_ids?: LocationIds;
  memory_type: MemoryType;
  model_revision?: ModelRevision;
  occurred_at: Timestamp;
  outcome_event_id: OutcomeEventId;
  outcome_summary: OutcomeSummary;
  owner_id: NonEmptyString;
  plan_ids?: PlanIds;
  policy_version: NonEmptyString;
  schema_version: SchemaVersion;
  silence_reason: SilenceReason;
  sources: Sources;
  summary: Summary;
  supersedes_id?: SupersedesId;
  tombstoned_at?: Timestamp | null;
  version: Version;
  world_id: NonEmptyString;
}
export interface ImportanceFeatures {
  contradiction?: number;
  goal_change?: number;
  irreversible?: number;
  novelty?: number;
  oracle_relevance?: number;
  personal_risk?: number;
  repetition?: number;
  resource_impact?: number;
}
export interface SourceReference {
  owner_id: NonEmptyString;
  source_id: NonEmptyString;
  source_type: SourceType;
  world_id: NonEmptyString;
}
