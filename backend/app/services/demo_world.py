"""Fixed, read-only demo world payloads."""

import json
from typing import TypeVar

from pydantic import BaseModel, ConfigDict

from app.domain.schemas import (
    ActionIntent,
    ActionResult,
    AgentBelief,
    AgentProfile,
    Character,
    Observation,
    OracleRequest,
    OracleResponse,
    World,
    WorldEvent,
)

T = TypeVar("T", bound=BaseModel)


def _from_json[T: BaseModel](model: type[T], payload: object) -> T:
    """Validate demo literals through the same JSON coercion path used by HTTP."""
    return model.model_validate_json(json.dumps(payload))


class DemoWorldReadModel(BaseModel):
    """HTTP read model for the fixed observer demo."""

    model_config = ConfigDict(extra="forbid", strict=True)

    world: World
    characters: list[Character]
    agentProfiles: list[AgentProfile]
    events: list[WorldEvent]
    observations: list[Observation]
    beliefs: list[AgentBelief]
    oracleRequests: list[OracleRequest]
    oracleResponses: list[OracleResponse]
    actionIntents: list[ActionIntent]
    actionResults: list[ActionResult]


class DemoWorldSummaryReadModel(BaseModel):
    """Narrow world fields safe for agent-scoped demo reads."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: str
    name: str
    current_time: str
    schema_version: str
    version: int


class DemoAgentPerspectiveReadModel(BaseModel):
    """HTTP read model for one fixed demo agent's local perspective."""

    model_config = ConfigDict(extra="forbid", strict=True)

    world: DemoWorldSummaryReadModel
    character: Character
    agentProfile: AgentProfile
    observations: list[Observation]
    beliefs: list[AgentBelief]
    oracleRequests: list[OracleRequest]
    oracleResponses: list[OracleResponse]
    actionIntents: list[ActionIntent]
    actionResults: list[ActionResult]


class DemoAgentInputReadModel(BaseModel):
    """Demo agent-facing input feed composed only of allowed observations."""

    model_config = ConfigDict(extra="forbid", strict=True)

    world: DemoWorldSummaryReadModel
    character: Character
    agentProfile: AgentProfile
    observations: list[Observation]


def get_gray_harbor_demo_world() -> DemoWorldReadModel:
    """Return the fixed Gray Harbor observer payload without infrastructure access."""
    world = _from_json(
        World,
        {
            "id": "world-gray-harbor-lockdown",
            "name": "Gray Harbor Lockdown Zone",
            "description": "A fixed seven-day lockdown demo slice for observing objective facts, partial observations, subjective beliefs, player revelation, and action adjudication.",  # noqa: E501
            "status": "running",
            "current_time": "2026-07-25T06:40:00+08:00",
            "time_scale": 1.0,
            "version": 1,
            "schema_version": "1.0",
            "created_at": "2026-07-23T08:00:00+08:00",
            "updated_at": "2026-07-25T06:40:00+08:00",
        },
    )
    characters = [
        _from_json(
            Character,
            {
                "id": "char-lin-zhixia",
                "world_id": world.id,
                "name": "Lin Zhixia",
                "description": "Community clinic doctor seeing fever cases before she has full government context.",  # noqa: E501
                "location_id": "clinic-east",
                "occupation": "Community clinic doctor",
                "age": 34,
                "status": "active",
                "is_special_agent": True,
                "health": 0.86,
                "resources": {"masks": 12, "medicine_days": 2},
                "version": 1,
                "schema_version": "1.0",
                "created_at": "2026-07-23T08:00:00+08:00",
                "updated_at": "2026-07-25T06:40:00+08:00",
            },
        ),
        _from_json(
            Character,
            {
                "id": "char-zhou-qiming",
                "world_id": world.id,
                "name": "Zhou Qiming",
                "description": "District official who knows part of the lockdown plan but not the clinic pressure.",  # noqa: E501
                "location_id": "district-office",
                "occupation": "District operations officer",
                "age": 41,
                "status": "active",
                "is_special_agent": True,
                "health": 0.92,
                "resources": {"clearance_level": "restricted", "radio": True},
                "version": 1,
                "schema_version": "1.0",
                "created_at": "2026-07-23T08:00:00+08:00",
                "updated_at": "2026-07-25T06:40:00+08:00",
            },
        ),
        _from_json(
            Character,
            {
                "id": "char-chen-mo",
                "world_id": world.id,
                "name": "Chen Mo",
                "description": "Convenience store owner piecing together the situation from customers, couriers, and street changes.",  # noqa: E501
                "location_id": "north-market-store",
                "occupation": "Convenience store owner",
                "age": 29,
                "status": "active",
                "is_special_agent": True,
                "health": 0.78,
                "resources": {"water_boxes": 2, "food_days": 3, "child_medicine_days": 1},
                "version": 1,
                "schema_version": "1.0",
                "created_at": "2026-07-23T08:00:00+08:00",
                "updated_at": "2026-07-25T06:40:00+08:00",
            },
        ),
    ]
    agent_profiles = [
        _from_json(
            AgentProfile,
            {
                "character_id": character.id,
                "persona_summary": f"{character.name} is a special demo agent with isolated local knowledge.",  # noqa: E501
                "traits": {"caution": 0.7, "initiative": 0.6},
                "values": {"safety": 0.9, "truthfulness": 0.7},
                "desires": ["protect dependents", "understand local risk"],
                "fears": ["acting on false information"],
                "taboos": ["treat player revelation as a command"],
                "abilities": ["observe", "wait", "speak"],
                "decision_biases": {"confirm_before_risk": 0.8},
                "oracle_relationship": {"kind": "advice_only"},
                "wake_policy": {"mode": "fixed_demo"},
                "schema_version": "1.0",
            },
        )
        for character in characters
    ]
    events = [
        _from_json(
            WorldEvent,
            {
                "id": "event-day1-fever",
                "world_id": world.id,
                "event_type": "system",
                "title": "Harbor hospital reports unusual fever cases",
                "description": "Day 1 08:00: the harbor hospital reports abnormal fever cases to the health bureau.",  # noqa: E501
                "occurred_at": "2026-07-23T08:00:00+08:00",
                "location_id": "harbor-hospital",
                "participant_ids": ["char-lin-zhixia"],
                "fact_ids": ["fact-fever-cluster"],
                "source_action_id": None,
                "visibility": "restricted",
                "correlation_id": "corr-fever-cluster",
                "metadata": {"day": 1, "hour": "08:00"},
                "schema_version": "1.0",
                "created_at": "2026-07-23T08:01:00+08:00",
            },
        ),
        _from_json(
            WorldEvent,
            {
                "id": "event-day1-pathogen",
                "world_id": world.id,
                "event_type": "system",
                "title": "Health bureau confirms fast spread internally",
                "description": "Day 1 13:00: internal analysis says transmission is faster than expected.",  # noqa: E501
                "occurred_at": "2026-07-23T13:00:00+08:00",
                "location_id": "health-bureau",
                "participant_ids": [],
                "fact_ids": ["fact-fast-spread"],
                "source_action_id": None,
                "visibility": "secret",
                "correlation_id": "corr-health-bureau",
                "metadata": {"day": 1, "hour": "13:00"},
                "schema_version": "1.0",
                "created_at": "2026-07-23T13:03:00+08:00",
            },
        ),
        _from_json(
            WorldEvent,
            {
                "id": "event-day2-panic-buying",
                "world_id": world.id,
                "event_type": "state_changed",
                "title": "Panic buying appears in north market",
                "description": "Day 2 09:00: several supermarkets report shortages and slower restocking.",  # noqa: E501
                "occurred_at": "2026-07-24T09:00:00+08:00",
                "location_id": "north-market",
                "participant_ids": ["char-chen-mo"],
                "fact_ids": ["fact-panic-buying"],
                "source_action_id": None,
                "visibility": "public",
                "correlation_id": "corr-market-shortage",
                "metadata": {"day": 2, "hour": "09:00"},
                "schema_version": "1.0",
                "created_at": "2026-07-24T09:05:00+08:00",
            },
        ),
        _from_json(
            WorldEvent,
            {
                "id": "event-day2-north-gate-plan",
                "world_id": world.id,
                "event_type": "system",
                "title": "City hall secretly approves north gate lockdown plan",
                "description": "Day 2 18:00: the plan is approved internally before public announcement.",  # noqa: E501
                "occurred_at": "2026-07-24T18:00:00+08:00",
                "location_id": "city-hall",
                "participant_ids": ["char-zhou-qiming"],
                "fact_ids": ["fact-north-gate-plan"],
                "source_action_id": None,
                "visibility": "secret",
                "correlation_id": "corr-north-gate-plan",
                "metadata": {"day": 2, "hour": "18:00"},
                "schema_version": "1.0",
                "created_at": "2026-07-24T18:06:00+08:00",
            },
        ),
        _from_json(
            WorldEvent,
            {
                "id": "event-day3-guards",
                "world_id": world.id,
                "event_type": "movement",
                "title": "Additional guards arrive at north gate",
                "description": "Day 3 06:00: guards deploy before any public notice is posted.",
                "occurred_at": "2026-07-25T06:00:00+08:00",
                "location_id": "north-gate",
                "participant_ids": ["char-zhou-qiming"],
                "fact_ids": ["fact-north-gate-guards"],
                "source_action_id": None,
                "visibility": "restricted",
                "correlation_id": "corr-north-gate-guards",
                "metadata": {"day": 3, "hour": "06:00"},
                "schema_version": "1.0",
                "created_at": "2026-07-25T06:02:00+08:00",
            },
        ),
        _from_json(
            WorldEvent,
            {
                "id": "event-chen-action-result",
                "world_id": world.id,
                "event_type": "state_changed",
                "title": "Chen Mo delays going to north gate",
                "description": "The courier does not answer, but Chen Mo checks supplies and stays in the store for now.",  # noqa: E501
                "occurred_at": "2026-07-25T06:38:00+08:00",
                "location_id": "north-market-store",
                "participant_ids": ["char-chen-mo"],
                "fact_ids": ["fact-chen-delays-north-gate"],
                "source_action_id": "intent-chen-contact-courier",
                "visibility": "private",
                "correlation_id": "corr-chen-oracle-decision",
                "metadata": {"day": 3, "hour": "06:38"},
                "schema_version": "1.0",
                "created_at": "2026-07-25T06:39:00+08:00",
            },
        ),
    ]
    observations = [
        _from_json(
            Observation,
            {
                "id": "obs-lin-fever",
                "world_id": world.id,
                "agent_id": "char-lin-zhixia",
                "observed_at": "2026-07-23T08:20:00+08:00",
                "observation_type": "mixed",
                "source_event_id": "event-day1-fever",
                "source_message_id": None,
                "visible_entities": [
                    {
                        "entity": {"entity_type": "location", "entity_id": "clinic-east"},
                        "name": "Clinic waiting area",
                        "description": "More fever patients are waiting than usual.",
                        "attributes": {"crowding": "high"},
                    }
                ],
                "heard_statements": [
                    {
                        "speaker_id": None,
                        "content": "People say the harbor hospital has similar cases.",
                    }
                ],
                "received_messages": [],
                "felt_changes": [
                    {"description": "Medicine consumption is rising quickly.", "intensity": 0.7}
                ],
                "available_actions": [
                    {
                        "action_type": "speak",
                        "description": "Warn neighbors to reduce gatherings.",
                        "parameter_hints": {},
                    }
                ],
                "metadata": {"perspective_note": "Does not know the north gate lockdown plan."},
                "schema_version": "1.0",
            },
        ),
        _from_json(
            Observation,
            {
                "id": "obs-zhou-plan",
                "world_id": world.id,
                "agent_id": "char-zhou-qiming",
                "observed_at": "2026-07-24T18:18:00+08:00",
                "observation_type": "message",
                "source_event_id": "event-day2-north-gate-plan",
                "source_message_id": "msg-city-hall-plan",
                "visible_entities": [],
                "heard_statements": [],
                "received_messages": [
                    {
                        "message_id": "msg-city-hall-plan",
                        "sender_id": None,
                        "sent_at": "2026-07-24T18:12:00+08:00",
                        "content": "North gate controls are in preparation; wait for public wording.",  # noqa: E501
                    }
                ],
                "felt_changes": [
                    {"description": "The office switches to low-voice calls.", "intensity": 0.5}
                ],
                "available_actions": [
                    {
                        "action_type": "wait",
                        "description": "Wait for formal announcement.",
                        "parameter_hints": {},
                    }
                ],
                "metadata": {"perspective_note": "Does not know actual clinic bed pressure."},
                "schema_version": "1.0",
            },
        ),
        _from_json(
            Observation,
            {
                "id": "obs-chen-rumor",
                "world_id": world.id,
                "agent_id": "char-chen-mo",
                "observed_at": "2026-07-25T06:12:00+08:00",
                "observation_type": "auditory",
                "source_event_id": "event-day3-guards",
                "source_message_id": None,
                "visible_entities": [
                    {
                        "entity": {"entity_type": "location", "entity_id": "north-market-street"},
                        "name": "North market street",
                        "description": "Some people hurry toward north gate while others tell them to turn back.",  # noqa: E501
                        "attributes": {"visibility": "partial"},
                    }
                ],
                "heard_statements": [
                    {"speaker_id": None, "content": "North gate may already be closed."},
                    {"speaker_id": None, "content": "The guards might only be changing shifts."},
                ],
                "received_messages": [],
                "felt_changes": [
                    {"description": "Customers in the store are visibly anxious.", "intensity": 0.8}
                ],
                "available_actions": [
                    {
                        "action_type": "custom",
                        "description": "Ask the player for a revelation.",
                        "parameter_hints": {},
                    }
                ],
                "metadata": {"perspective_note": "Only hears rumors and sees street changes."},
                "schema_version": "1.0",
            },
        ),
    ]
    beliefs = [
        _from_json(
            AgentBelief,
            {
                "id": "belief-lin-fever-risk",
                "world_id": world.id,
                "agent_id": "char-lin-zhixia",
                "subject": "Fever cases",
                "predicate": "are increasing abnormally",
                "object": "clinic and hospital may both be under pressure",
                "confidence": 0.78,
                "source_type": "observation",
                "source_id": "obs-lin-fever",
                "learned_at": "2026-07-23T08:25:00+08:00",
                "last_updated_at": "2026-07-24T09:00:00+08:00",
                "schema_version": "1.0",
            },
        ),
        _from_json(
            AgentBelief,
            {
                "id": "belief-zhou-north-gate",
                "world_id": world.id,
                "agent_id": "char-zhou-qiming",
                "subject": "North gate",
                "predicate": "may enter controlled access",
                "object": "cannot confirm to residents before announcement",
                "confidence": 0.86,
                "source_type": "message",
                "source_id": "msg-city-hall-plan",
                "learned_at": "2026-07-24T18:18:00+08:00",
                "last_updated_at": "2026-07-25T06:00:00+08:00",
                "schema_version": "1.0",
            },
        ),
        _from_json(
            AgentBelief,
            {
                "id": "belief-chen-lockdown-started",
                "world_id": world.id,
                "agent_id": "char-chen-mo",
                "subject": "North gate lockdown",
                "predicate": "may have started",
                "object": "must decide whether to leave with child",
                "confidence": 0.42,
                "source_type": "observation",
                "source_id": "obs-chen-rumor",
                "learned_at": "2026-07-25T06:12:00+08:00",
                "last_updated_at": "2026-07-25T06:22:00+08:00",
                "schema_version": "1.0",
            },
        ),
    ]
    oracle_request = _from_json(
        OracleRequest,
        {
            "id": "oracle-request-chen-north-gate",
            "world_id": world.id,
            "agent_id": "char-chen-mo",
            "question": "Should I take my child toward north gate or wait in the store?",
            "context_summary": "Chen Mo hears north gate rumors, has limited supplies, and the child needs medicine.",  # noqa: E501
            "requested_at": "2026-07-25T06:20:00+08:00",
            "world_deadline": "2026-07-25T07:00:00+08:00",
            "real_deadline": None,
            "status": "answered",
            "decision_correlation_id": "corr-chen-oracle-decision",
            "schema_version": "1.0",
        },
    )
    oracle_response = _from_json(
        OracleResponse,
        {
            "id": "oracle-response-chen-north-gate",
            "request_id": oracle_request.id,
            "world_id": world.id,
            "agent_id": "char-chen-mo",
            "content": "Do not rush to north gate yet; confirm medicine and food, then find a trusted person to verify guard movement.",  # noqa: E501
            "clarity": 0.74,
            "responded_at": "2026-07-25T06:27:00+08:00",
            "schema_version": "1.0",
        },
    )
    action_intent = _from_json(
        ActionIntent,
        {
            "id": "intent-chen-contact-courier",
            "world_id": world.id,
            "actor_id": "char-chen-mo",
            "action_type": "custom",
            "parameters": {
                "target": "courier-friend",
                "preparation": ["call_courier", "count_food", "delay_north_gate"],
            },
            "reason_summary": "Chen Mo treats the player revelation as advice, tries to contact a courier, and checks three days of supplies.",  # noqa: E501
            "submitted_at": "2026-07-25T06:31:00+08:00",
            "expected_duration": 0.4,
            "correlation_id": "corr-chen-oracle-decision",
            "schema_version": "1.0",
        },
    )
    action_result = _from_json(
        ActionResult,
        {
            "id": "result-chen-contact-courier",
            "world_id": world.id,
            "action_id": action_intent.id,
            "actor_id": "char-chen-mo",
            "status": "succeeded",
            "started_at": "2026-07-25T06:32:00+08:00",
            "completed_at": "2026-07-25T06:38:00+08:00",
            "failure_code": None,
            "failure_reason": None,
            "state_changes": [
                {
                    "entity_type": "character",
                    "entity_id": "char-chen-mo",
                    "field": "resources.water_boxes",
                    "old_value": "unknown",
                    "new_value": 2,
                }
            ],
            "generated_event_ids": ["event-chen-action-result"],
            "witness_character_ids": ["char-chen-mo"],
            "correlation_id": "corr-chen-oracle-decision",
            "schema_version": "1.0",
        },
    )
    return DemoWorldReadModel(
        world=world,
        characters=characters,
        agentProfiles=agent_profiles,
        events=events,
        observations=observations,
        beliefs=beliefs,
        oracleRequests=[oracle_request],
        oracleResponses=[oracle_response],
        actionIntents=[action_intent],
        actionResults=[action_result],
    )


def get_gray_harbor_agent_perspective(
    agent_id: str,
) -> DemoAgentPerspectiveReadModel | None:
    """Return one demo agent's local read model, or None when the agent is unknown."""
    demo_world = get_gray_harbor_demo_world()
    character = next(
        (candidate for candidate in demo_world.characters if candidate.id == agent_id),
        None,
    )
    agent_profile = next(
        (candidate for candidate in demo_world.agentProfiles if candidate.character_id == agent_id),
        None,
    )
    if character is None or agent_profile is None:
        return None

    return DemoAgentPerspectiveReadModel(
        world=DemoWorldSummaryReadModel(
            id=demo_world.world.id,
            name=demo_world.world.name,
            current_time=demo_world.world.current_time.isoformat(),
            schema_version=demo_world.world.schema_version,
            version=demo_world.world.version,
        ),
        character=character,
        agentProfile=agent_profile,
        observations=[
            observation
            for observation in demo_world.observations
            if observation.agent_id == agent_id
        ],
        beliefs=[belief for belief in demo_world.beliefs if belief.agent_id == agent_id],
        oracleRequests=[
            request for request in demo_world.oracleRequests if request.agent_id == agent_id
        ],
        oracleResponses=[
            response for response in demo_world.oracleResponses if response.agent_id == agent_id
        ],
        actionIntents=[
            intent for intent in demo_world.actionIntents if intent.actor_id == agent_id
        ],
        actionResults=[
            result for result in demo_world.actionResults if result.actor_id == agent_id
        ],
    )
