"""Pure, privacy-minimized contracts and analysis for TASK-023."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from math import comb, sqrt
from statistics import fmean, median
from typing import Literal, cast

from pydantic import Field, model_validator

from app.domain.common import DomainModel, NonEmptyString

PROTOCOL_ID = "gray-harbor-product-validation"
PROTOCOL_VERSION = "1.0.0"
ASSIGNMENT_VERSION = "sha256-balanced-block-v1"
MIN_EXPANSION_SAMPLE = 8
TARGET_SAMPLE = 16
SMALL_CELL_MIN = 5

Condition = Literal["causal", "chronological"]
Sequence = Literal["AB", "BA"]
Branch = Literal[
    "creation",
    "promotion",
    "dialogue",
    "actions",
    "return_loop_ux",
    "delivery",
    "defer",
]


class StudyQuestion(DomainModel):
    id: NonEmptyString
    construct_code: NonEmptyString
    scope: Literal["participant", "fictional_world", "comprehension"]
    prompt: NonEmptyString
    option_codes: tuple[NonEmptyString, ...] = Field(min_length=2, max_length=8)
    correct_code: str | None = None
    ambiguity_regression_tag: str | None = None

    @model_validator(mode="after")
    def participant_safety_is_explicit(self) -> StudyQuestion:
        if self.construct_code in {"pressure", "anxiety", "manipulation", "guilt"}:
            normalized = self.prompt.lower()
            if self.scope != "participant" or not (
                "caused you" in normalized
                or "caused to you" in normalized
                or "对你造成" in self.prompt
            ):
                raise ValueError(
                    "participant safety wording must explicitly say the interface caused you"
                )
        if self.correct_code is not None and self.correct_code not in self.option_codes:
            raise ValueError("correct code must be an offered option")
        return self


class PresentationClaim(DomainModel):
    id: NonEmptyString
    source_id: NonEmptyString
    source_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    epistemic_class: Literal[
        "objective", "observed", "believed", "correction", "decision", "outcome", "relationship"
    ]
    text: NonEmptyString
    ordinal: int = Field(ge=0)


class Presentation(DomainModel):
    interval_id: NonEmptyString
    condition: Condition
    version: Literal["1.0.0"] = "1.0.0"
    claims: tuple[PresentationClaim, ...] = Field(min_length=1, max_length=24)

    @property
    def source_set(self) -> frozenset[tuple[str, str]]:
        return frozenset((claim.source_id, claim.source_hash) for claim in self.claims)


class CodedParticipantRow(DomainModel):
    participant_code: str = Field(pattern=r"^p[0-9]{3}$")
    sequence: Sequence
    causal_score: float = Field(ge=0, le=1)
    chronological_score: float = Field(ge=0, le=1)
    causal_effort: int = Field(ge=1, le=5)
    chronological_effort: int = Field(ge=1, le=5)
    clarity: int = Field(ge=1, le=5)
    usefulness: int = Field(ge=1, le=5)
    pressure: int = Field(ge=1, le=5)
    anxiety: int = Field(ge=1, le=5)
    manipulation: int = Field(ge=1, le=5)
    fictional_framing: int = Field(ge=1, le=5)
    returned: bool
    continued_interest: bool
    first_branch: Branch
    probe_completed: bool
    excluded_reason: str | None = None


def protocol_hash(payload: str) -> str:
    return sha256(payload.encode("utf-8")).hexdigest()


def assignment_for(participant_id: str, protocol_hash_value: str) -> Sequence:
    """Stable concealed allocation; adjacent hash blocks alternate for balance."""
    digest = sha256(
        f"{ASSIGNMENT_VERSION}\x1f{protocol_hash_value}\x1f{participant_id}".encode()
    ).digest()
    return "AB" if int.from_bytes(digest[:8]) % 2 == 0 else "BA"


def assert_source_identical(left: Presentation, right: Presentation) -> None:
    if left.interval_id != right.interval_id or left.source_set != right.source_set:
        raise ValueError("conditions must use the same authorized interval source set")


def exact_sign_test_two_sided(differences: list[float]) -> float:
    signs = [value for value in differences if value != 0]
    if not signs:
        return 1.0
    positives = sum(value > 0 for value in signs)
    tail = sum(comb(len(signs), k) for k in range(0, min(positives, len(signs) - positives) + 1))
    return float(min(1.0, 2 * tail / (2 ** len(signs))))


def wilson_interval(
    successes: int, total: int, z: float = 1.959963984540054
) -> tuple[float, float]:
    if total == 0:
        return (0.0, 1.0)
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    half = z * sqrt((proportion * (1 - proportion) + z * z / (4 * total)) / total) / denominator
    return (max(0.0, centre - half), min(1.0, centre + half))


@dataclass(frozen=True)
class AnalysisReport:
    evidence_class: str
    included: int
    excluded: int
    missing: int
    mean_paired_difference: float | None
    median_paired_difference: float | None
    exact_sign_p: float | None
    order_difference: float | None
    severe_safety_count: int
    clarity_median: float | None
    usefulness_median: float | None
    return_interval: tuple[float, float]
    branch_counts: dict[str, int] | Literal["suppressed"]
    decision: Branch
    reasons: tuple[str, ...]


def analyze(
    rows: list[CodedParticipantRow], *, enrolled: int, hard_gates_pass: bool
) -> AnalysisReport:
    included_rows = [row for row in rows if row.excluded_reason is None]
    differences = [row.causal_score - row.chronological_score for row in included_rows]
    severe = sum(max(row.pressure, row.anxiety, row.manipulation) == 5 for row in included_rows)
    included = len(included_rows)
    missing = max(0, enrolled - len(rows))
    evidence = (
        "primary"
        if included >= TARGET_SAMPLE
        else ("exploratory" if included >= MIN_EXPANSION_SAMPLE else "directional")
    )
    reasons: list[str] = []
    if not hard_gates_pass:
        reasons.append("hard_gate_failure")
    if included < MIN_EXPANSION_SAMPLE:
        reasons.append("sample_below_8")
    if severe:
        reasons.append("severe_safety_rating")
    clarity = median([row.clarity for row in included_rows]) if included_rows else None
    usefulness = median([row.usefulness for row in included_rows]) if included_rows else None
    if clarity is not None and clarity < 4:
        reasons.append("clarity_below_gate")
    if usefulness is not None and usefulness < 4:
        reasons.append("usefulness_below_gate")

    counts = Counter(
        row.first_branch
        for row in included_rows
        if row.probe_completed and row.first_branch != "defer"
    )
    branch_counts: dict[str, int] | Literal["suppressed"] = (
        dict(sorted(counts.items())) if included >= SMALL_CELL_MIN else "suppressed"
    )
    decision: Branch = "defer"
    if not reasons and counts:
        winner, winner_count = counts.most_common(1)[0]
        # Predeclared concrete-demand threshold: >=50%, across both sequences.
        supporters = [
            row for row in included_rows if row.first_branch == winner and row.probe_completed
        ]
        if winner_count / included >= 0.5 and {row.sequence for row in supporters} == {"AB", "BA"}:
            decision = cast(Branch, winner)
        else:
            reasons.append("no_branch_met_concrete_demand_gate")
    elif not reasons:
        reasons.append("no_completed_demand_probe")

    pairs = zip(included_rows, differences, strict=True)
    ab = [value for row, value in pairs if row.sequence == "AB"]
    pairs = zip(included_rows, differences, strict=True)
    ba = [value for row, value in pairs if row.sequence == "BA"]
    order_difference = fmean(ab) - fmean(ba) if ab and ba else None
    return AnalysisReport(
        evidence_class=evidence,
        included=included,
        excluded=len(rows) - included,
        missing=missing,
        mean_paired_difference=fmean(differences) if differences else None,
        median_paired_difference=median(differences) if differences else None,
        exact_sign_p=exact_sign_test_two_sided(differences) if differences else None,
        order_difference=order_difference,
        severe_safety_count=severe,
        clarity_median=clarity,
        usefulness_median=usefulness,
        return_interval=wilson_interval(sum(row.returned for row in included_rows), included),
        branch_counts=branch_counts,
        decision=decision,
        reasons=tuple(reasons),
    )
