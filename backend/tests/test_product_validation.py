import pytest
from pydantic import ValidationError

from app.domain.product_validation import (
    CodedParticipantRow,
    Presentation,
    PresentationClaim,
    StudyQuestion,
    analyze,
    assert_source_identical,
    assignment_for,
    protocol_hash,
)


def test_assignment_is_stable_and_reasonably_balanced() -> None:
    frozen = protocol_hash("protocol-1")
    assignments = [assignment_for(f"participant-{index}", frozen) for index in range(3200)]
    assert assignments == [assignment_for(f"participant-{index}", frozen) for index in range(3200)]
    assert abs(assignments.count("AB") - assignments.count("BA")) < 160


def test_source_identity_rejects_hidden_condition_difference() -> None:
    claim = PresentationClaim(
        id="claim-1",
        source_id="source-1",
        source_hash="a" * 64,
        epistemic_class="decision",
        text="Chen rejected the suggestion.",
        ordinal=0,
    )
    causal = Presentation(interval_id="i1", condition="causal", claims=(claim,))
    chronological = Presentation(interval_id="i1", condition="chronological", claims=(claim,))
    assert_source_identical(causal, chronological)
    changed = chronological.model_copy(
        update={"claims": (claim.model_copy(update={"source_hash": "b" * 64}),)}
    )
    with pytest.raises(ValueError, match="same authorized"):
        assert_source_identical(causal, changed)


def test_ambiguous_task_022_safety_wording_fails() -> None:
    with pytest.raises(ValidationError, match="explicitly"):
        StudyQuestion(
            id="pressure",
            construct_code="pressure",
            scope="fictional_world",
            prompt="How pressured was the situation?",
            option_codes=("1", "2", "3", "4", "5"),
            ambiguity_regression_tag="task-022",
        )
    corrected = StudyQuestion(
        id="pressure",
        construct_code="pressure",
        scope="participant",
        prompt="How much pressure was caused to you by this interface?",
        option_codes=("1", "2", "3", "4", "5"),
        ambiguity_regression_tag="task-022-corrected",
    )
    assert corrected.scope == "participant"


def test_analysis_defer_is_mandatory_below_eight_and_suppresses_cells() -> None:
    row = CodedParticipantRow(
        participant_code="p001",
        sequence="AB",
        causal_score=1,
        chronological_score=0.8,
        causal_effort=2,
        chronological_effort=3,
        clarity=5,
        usefulness=5,
        pressure=1,
        anxiety=1,
        manipulation=1,
        fictional_framing=5,
        returned=True,
        continued_interest=True,
        first_branch="creation",
        probe_completed=True,
    )
    report = analyze([row], enrolled=1, hard_gates_pass=True)
    assert report.evidence_class == "directional"
    assert report.decision == "defer"
    assert report.branch_counts == "suppressed"
    assert "sample_below_8" in report.reasons


def test_no_low_rating_is_silently_excluded() -> None:
    rows = [
        CodedParticipantRow(
            participant_code=f"p{index:03}",
            sequence="AB" if index % 2 else "BA",
            causal_score=0.8,
            chronological_score=0.7,
            causal_effort=2,
            chronological_effort=3,
            clarity=3 if index == 1 else 5,
            usefulness=5,
            pressure=1,
            anxiety=1,
            manipulation=1,
            fictional_framing=5,
            returned=True,
            continued_interest=True,
            first_branch="dialogue",
            probe_completed=True,
        )
        for index in range(1, 9)
    ]
    report = analyze(rows, enrolled=8, hard_gates_pass=True)
    assert report.included == 8
    assert report.excluded == 0
