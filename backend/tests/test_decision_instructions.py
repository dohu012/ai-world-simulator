"""Persona instruction composition for agent decisions."""

from datetime import UTC, datetime

from app.application.agent_decision import PROMPT_VERSION, build_decision_instructions
from app.application.memory_service import (
    CandidateRead,
    MemoryRead,
    RetrievalRead,
    ScoreComponents,
)
from app.services.demo_world import get_gray_harbor_agent_perspective


def retrieval_with(summaries: list[tuple[str, bool]]) -> RetrievalRead:
    scores = ScoreComponents.model_validate(
        {
            key: 0.5
            for key in (
                "lexical",
                "semantic",
                "recency",
                "importance",
                "goal",
                "entity",
                "location",
                "emotion",
                "contradiction",
                "oracle",
                "diversity_penalty",
                "total",
            )
        }
    )
    return RetrievalRead(
        id="retrieval-test",
        policy_version="memory-policy-v1",
        mode="lexical",
        context_watermark="b" * 64,
        character_budget=4000,
        characters_used=100,
        candidates=[
            CandidateRead(
                memory=MemoryRead(
                    id=f"memory-{index}",
                    memory_type="event",
                    summary=summary,
                    occurred_at=datetime(2026, 8, 1, tzinfo=UTC),
                    importance=0.8,
                    confidence=0.9,
                    source_count=1,
                    embedding_status="ready",
                    superseded=False,
                ),
                rank=index,
                selected=selected,
                exclusion_reason="" if selected else "budget",
                scores=scores,
            )
            for index, (summary, selected) in enumerate(summaries, start=1)
        ],
    )


def test_instructions_carry_identity_persona_memory_and_relationships() -> None:
    perspective = get_gray_harbor_agent_perspective("char-chen-mo")
    assert perspective is not None
    memory_context = retrieval_with(
        [("The courier warned me about the north gate.", True), ("Excluded noise.", False)]
    )
    evolution_context = {
        "identity": {"persona_summary": "I have grown wary of official reassurances."},
        "relationships": [
            {
                "target_type": "character",
                "target_id": "char-lin-zhixia",
                "interpretation": "I trust Lin Zhixia with my child's safety.",
            }
        ],
    }
    text = build_decision_instructions(
        perspective.character,
        perspective.agentProfile,
        memory_context,
        evolution_context,
    )
    assert f"You are {perspective.character.name}" in text
    assert perspective.agentProfile.persona_summary in text
    assert "The courier warned me about the north gate." in text
    assert "Excluded noise." not in text
    assert "I have grown wary of official reassurances." in text
    assert "I trust Lin Zhixia with my child's safety." in text
    assert "Choose exactly one entry" in text


def test_instructions_omit_empty_sections_and_version_bumped() -> None:
    perspective = get_gray_harbor_agent_perspective("char-chen-mo")
    assert perspective is not None
    text = build_decision_instructions(
        perspective.character,
        perspective.agentProfile,
        retrieval_with([]),
        {},
    )
    assert "Memories that feel relevant" not in text
    assert "Relationship with" not in text
    assert text.startswith(f"You are {perspective.character.name}")
    assert PROMPT_VERSION == "gray-harbor-decision-v3"
