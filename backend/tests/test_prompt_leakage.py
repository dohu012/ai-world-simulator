"""Decoy-secret leakage tests over the assembled model prompt.

The isolation guarantee is only real if it holds on the exact bytes handed to the
provider. Each test plants a decoy the acting agent must not know, then asserts
the decoy never appears anywhere in `ModelRequest.prompt` or `.instructions` —
not in observations, not in memory context, not in evolution context, and not
mirrored back through an affordance parameter.
"""

import json
from datetime import UTC, datetime

from app.application.agent_decision import (
    INPUT_VERSION,
    build_decision_instructions,
    build_decision_prompt,
)
from app.application.memory_service import (
    CandidateRead,
    MemoryRead,
    RetrievalRead,
    ScoreComponents,
)
from app.application.observation_builder import ObservationBuilder
from app.services.demo_world import (
    DemoAgentInputReadModel,
    get_gray_harbor_agent_perspective,
    get_gray_harbor_demo_world,
)

ACTING_AGENT = "char-chen-mo"

# Decoys are phrased as the kind of content that would be genuinely damaging to
# leak: another character's private reasoning, a world-authoring fact the agent
# has no channel to, and a memory that belongs to somebody else.
OTHER_AGENT_SECRET = "DECOY-ZHOU-PRIVATE-city-hall-approved-the-lockdown-at-1800"
WORLD_AUTHORING_SECRET = "DECOY-GROUNDTRUTH-pathogen-r0-is-4point1"
OTHER_AGENT_MEMORY = "DECOY-LIN-MEMORY-the-clinic-has-seven-doses-left"

ALL_DECOYS = (OTHER_AGENT_SECRET, WORLD_AUTHORING_SECRET, OTHER_AGENT_MEMORY)


def empty_retrieval() -> RetrievalRead:
    return RetrievalRead(
        id="retrieval-leakage-test",
        policy_version="memory-policy-v1",
        mode="lexical",
        context_watermark="c" * 64,
        character_budget=4000,
        characters_used=0,
        candidates=[],
    )


def scores() -> ScoreComponents:
    return ScoreComponents.model_validate(
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


def retrieval_with_unselected(summary: str) -> RetrievalRead:
    """A candidate the packer scored but excluded from the budget."""
    return RetrievalRead(
        id="retrieval-leakage-test",
        policy_version="memory-policy-v1",
        mode="lexical",
        context_watermark="d" * 64,
        character_budget=4000,
        characters_used=10,
        candidates=[
            CandidateRead(
                memory=MemoryRead(
                    id="memory-decoy",
                    memory_type="event",
                    summary=summary,
                    occurred_at=datetime(2026, 8, 1, tzinfo=UTC),
                    importance=0.8,
                    confidence=0.9,
                    source_count=1,
                    embedding_status="ready",
                    superseded=False,
                ),
                rank=1,
                selected=False,
                exclusion_reason="budget",
                scores=scores(),
            )
        ],
    )


def agent_input(agent_id: str = ACTING_AGENT) -> DemoAgentInputReadModel:
    perspective = get_gray_harbor_agent_perspective(agent_id)
    assert perspective is not None
    return DemoAgentInputReadModel(
        world=perspective.world,
        character=perspective.character,
        agentProfile=perspective.agentProfile,
        observations=list(perspective.observations),
    )


def prompt_for(
    input_model: DemoAgentInputReadModel,
    memory_context: RetrievalRead | None = None,
    evolution_context: dict[str, object] | None = None,
) -> str:
    return build_decision_prompt(
        input_model,
        [item.id for item in input_model.observations],
        "e" * 64,
        memory_context or empty_retrieval(),
        evolution_context or {},
        [{"id": "wait", "action": "wait", "parameters": {}}],
    )


def test_planted_decoys_never_reach_the_assembled_prompt() -> None:
    """The whole demo world carries decoys; only Chen Mo's own view may survive."""
    demo = get_gray_harbor_demo_world()
    builder = ObservationBuilder()
    # Production routes event-day3-guards to Chen Mo as an extra recipient.
    recipients = {"event-day3-guards": ["char-chen-mo"]}

    # Derive the decoy targets from the builder itself rather than restating its
    # visibility rules here: poison exactly those events that deliver Chen Mo no
    # observation at all, so this stays honest as the world's events change.
    baseline = builder.build_for_events(
        demo.events, demo.characters, additional_recipients=recipients
    )
    delivered = {item.source_event_id for item in baseline if item.agent_id == ACTING_AGENT}
    unreachable = [event for event in demo.events if event.id not in delivered]
    assert unreachable, "the fixture must contain at least one event Chen Mo cannot see"

    poisoned_events = [
        event.model_copy(
            update={
                "title": f"{event.title} {OTHER_AGENT_SECRET}",
                "description": f"{event.description} {WORLD_AUTHORING_SECRET}",
            }
        )
        if event.id not in delivered
        else event
        for event in demo.events
    ]
    observations = builder.build_for_events(
        poisoned_events, demo.characters, additional_recipients=recipients
    )
    mine = [item for item in observations if item.agent_id == ACTING_AGENT]
    assert mine, "the acting agent must still receive its own observations"

    input_model = agent_input().model_copy(update={"observations": mine})
    prompt = prompt_for(input_model, retrieval_with_unselected(OTHER_AGENT_MEMORY))
    for decoy in ALL_DECOYS:
        assert decoy not in prompt, f"{decoy} leaked into the agent prompt"


def test_unselected_memory_candidate_body_never_reaches_prompt_or_instructions() -> None:
    memory_context = retrieval_with_unselected(OTHER_AGENT_MEMORY)
    input_model = agent_input()
    prompt = prompt_for(input_model, memory_context)
    instructions = build_decision_instructions(
        input_model.character, input_model.agentProfile, memory_context, {}
    )
    assert OTHER_AGENT_MEMORY not in prompt
    assert OTHER_AGENT_MEMORY not in instructions


def test_evolution_context_decoy_in_an_unread_field_never_reaches_instructions() -> None:
    """Only interpretations and persona summaries are narrated; raw offsets are not."""
    input_model = agent_input()
    evolution_context: dict[str, object] = {
        "identity": {
            "persona_summary": "I am wary.",
            "structured_state": {"private_note": OTHER_AGENT_SECRET},
        },
        "relationships": [
            {
                "target_type": "character",
                "target_id": "char-lin-zhixia",
                "interpretation": "I trust Lin.",
                "hidden_score": WORLD_AUTHORING_SECRET,
            }
        ],
    }
    instructions = build_decision_instructions(
        input_model.character, input_model.agentProfile, empty_retrieval(), evolution_context
    )
    assert "I am wary." in instructions
    assert "I trust Lin." in instructions
    for decoy in (OTHER_AGENT_SECRET, WORLD_AUTHORING_SECRET):
        assert decoy not in instructions


def test_prompt_carries_only_the_acting_agent_and_no_visibility_classes() -> None:
    demo = get_gray_harbor_demo_world()
    observations = ObservationBuilder().build_for_events(demo.events, demo.characters)
    mine = [item for item in observations if item.agent_id == ACTING_AGENT]
    input_model = agent_input().model_copy(update={"observations": mine})
    payload = json.loads(prompt_for(input_model))

    assert payload["input_version"] == INPUT_VERSION
    assert payload["character"]["id"] == ACTING_AGENT
    assert {item["agent_id"] for item in payload["observations"]} == {ACTING_AGENT}
    # No other character's identity is enumerated anywhere in agent input.
    others = {character.id for character in demo.characters if character.id != ACTING_AGENT} - set(
        payload["character"].get("relationships", []) or []
    )
    body = json.dumps(payload, ensure_ascii=False)
    for other in others:
        if any(other in json.dumps(item, ensure_ascii=False) for item in payload["observations"]):
            continue  # a co-witnessed event legitimately names its participants
        assert f'"{other}"' not in body.replace(
            json.dumps(payload["observations"], ensure_ascii=False), ""
        )
    # Visibility is a world-authoring class, never something an agent can read.
    for item in payload["observations"]:
        assert "source_visibility" not in item["metadata"]
    for banned in ("visibility", "fact_ids", "secret"):
        assert f'"{banned}"' not in body


def test_message_observations_expose_channel_but_not_its_reliability() -> None:
    from app.application.social_observation_builder import SocialObservationBuilder

    observation = SocialObservationBuilder().build_for_message(
        observation_id="obs-leak-check",
        world_id="world-gray-harbor-lockdown",
        recipient_id=ACTING_AGENT,
        message_id="message-leak-check",
        sender_id="char-lin-zhixia",
        body="The north gate may close tonight.",
        sent_at=datetime(2026, 7, 25, 6, tzinfo=UTC),
        delivered_at=datetime(2026, 7, 25, 6, 20, tzinfo=UTC),
        channel_kind="courier",
    )
    assert observation.metadata["channel_kind"] == "courier"
    assert "reliability" not in observation.metadata

    input_model = agent_input().model_copy(update={"observations": [observation]})
    assert "reliability" not in prompt_for(input_model)
