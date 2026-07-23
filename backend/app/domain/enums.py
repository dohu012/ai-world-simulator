"""Stable finite vocabularies used by the first domain contract version."""

from enum import StrEnum


class WorldStatus(StrEnum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CharacterStatus(StrEnum):
    ACTIVE = "active"
    INCAPACITATED = "incapacitated"
    MISSING = "missing"
    DEAD = "dead"
    INACTIVE = "inactive"


class FactVisibility(StrEnum):
    PUBLIC = "public"
    RESTRICTED = "restricted"
    SECRET = "secret"
    PRIVATE = "private"


class BeliefSourceType(StrEnum):
    OBSERVATION = "observation"
    MESSAGE = "message"
    MEMORY = "memory"
    INFERENCE = "inference"
    ORACLE = "oracle"
    UNKNOWN = "unknown"


class ObservationType(StrEnum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    MESSAGE = "message"
    ORACLE = "oracle"
    MIXED = "mixed"
    INTERNAL = "internal"


class ActionType(StrEnum):
    MOVE = "move"
    SPEAK = "speak"
    WAIT = "wait"
    CUSTOM = "custom"


class ActionStatus(StrEnum):
    ACCEPTED = "accepted"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class EventType(StrEnum):
    STATE_CHANGED = "state_changed"
    MOVEMENT = "movement"
    SPEECH = "speech"
    SCHEDULED_EVENT = "scheduled_event"
    SYSTEM = "system"


class OracleRequestStatus(StrEnum):
    PENDING = "pending"
    ANSWERED = "answered"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    RESOLVED = "resolved"
