from app.application.observation_builder import ObservationBuilder
from app.services.demo_world import get_gray_harbor_demo_world


def test_public_events_reach_all_agents_and_secret_events_do_not_leak() -> None:
    demo = get_gray_harbor_demo_world()
    observations = ObservationBuilder().build_for_events(demo.events, demo.characters)
    public_event = next(event for event in demo.events if event.visibility == "public")
    secret_without_participants = next(
        event for event in demo.events if event.visibility == "secret" and not event.participant_ids
    )
    assert {item.agent_id for item in observations if item.source_event_id == public_event.id} == {
        character.id for character in demo.characters
    }
    assert all(item.source_event_id != secret_without_participants.id for item in observations)


def test_restricted_additional_recipient_gets_indirect_observation_only() -> None:
    demo = get_gray_harbor_demo_world()
    observations = ObservationBuilder().build_for_events(
        demo.events,
        demo.characters,
        additional_recipients={"event-day3-guards": ["char-chen-mo"]},
    )
    chen = next(
        item
        for item in observations
        if item.source_event_id == "event-day3-guards" and item.agent_id == "char-chen-mo"
    )
    assert chen.observation_type == "auditory"
    assert chen.visible_entities == []
    assert len(chen.heard_statements) == 1
    assert chen.metadata["delivery"] == "indirect"


def test_private_event_reaches_only_participant() -> None:
    demo = get_gray_harbor_demo_world()
    observations = ObservationBuilder().build_for_events(demo.events, demo.characters)
    recipients = {
        item.agent_id for item in observations if item.source_event_id == "event-chen-action-result"
    }
    assert recipients == {"char-chen-mo"}


def test_oracle_response_becomes_agent_scoped_advice_observation() -> None:
    demo = get_gray_harbor_demo_world()
    observation = ObservationBuilder().build_for_oracle(
        demo.oracleRequests[0], demo.oracleResponses[0]
    )
    assert observation.id == "obs-oracle-response-chen-north-gate"
    assert observation.agent_id == "char-chen-mo"
    assert observation.observation_type == "oracle"
    assert observation.source_message_id == "oracle-response-chen-north-gate"
    assert observation.metadata["advice_only"] is True


def test_builder_is_deterministic() -> None:
    demo = get_gray_harbor_demo_world()
    builder = ObservationBuilder()
    first = builder.build_for_events(demo.events, demo.characters)
    second = builder.build_for_events(list(reversed(demo.events)), list(reversed(demo.characters)))
    assert first == second
