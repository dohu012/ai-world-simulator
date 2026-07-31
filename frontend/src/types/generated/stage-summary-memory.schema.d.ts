/* eslint-disable */
/** Generated from schemas/domain. Do not edit by hand. */

export type UnitFloat = number;
/**
 * @minItems 1
 * @maxItems 64
 */
export type ContributingMemoryIds = [NonEmptyString, ...NonEmptyString[]];
export type NonEmptyString = string;
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
export type MemoryType = "stage_summary";
export type ModelRevision = string | null;
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
export type TokenEstimate = number;
/**
 * @maxItems 32
 */
export type UnresolvedContradictionIds = NonEmptyString[];
export type Version = number;

export interface StageSummaryMemory {
  admission_score: UnitFloat;
  confidence: UnitFloat;
  contributing_memory_ids: ContributingMemoryIds;
  emotion_intensity?: number;
  emotion_labels?: EmotionLabels;
  ended_at?: Timestamp | null;
  epistemic_status: EpistemicStatus;
  goal_ids?: GoalIds;
  id: NonEmptyString;
  importance_features: ImportanceFeatures;
  involved_entity_ids?: InvolvedEntityIds;
  location_ids?: LocationIds;
  memory_type: MemoryType;
  model_revision?: ModelRevision;
  occurred_at: Timestamp;
  owner_id: NonEmptyString;
  plan_ids?: PlanIds;
  policy_version: NonEmptyString;
  schema_version: SchemaVersion;
  sources: Sources;
  stage_id: NonEmptyString;
  summary: Summary;
  supersedes_id?: SupersedesId;
  token_estimate: TokenEstimate;
  tombstoned_at?: Timestamp | null;
  unresolved_contradiction_ids?: UnresolvedContradictionIds;
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
