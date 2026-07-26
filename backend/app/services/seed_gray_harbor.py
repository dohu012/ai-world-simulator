"""Idempotently seed the fixed Gray Harbor world into PostgreSQL."""

import asyncio
from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.observation_builder import ObservationBuilder
from app.core.config import get_settings
from app.domain.enums import CharacterStatus, FactVisibility
from app.domain.schemas import Character, WorldFact
from app.infrastructure.database import models as r
from app.infrastructure.database.session import Database
from app.services.demo_world import get_gray_harbor_demo_world


def _payload(model: BaseModel) -> dict[str, object]:
    return model.model_dump(mode="json")


async def _upsert(
    session: AsyncSession,
    record_type: Any,
    values: Iterable[dict[str, object]],
    key: str = "id",
) -> None:
    rows = list(values)
    if not rows:
        return
    statement = insert(record_type).values(rows)
    updates = {
        column.name: getattr(statement.excluded, column.name)
        for column in record_type.__table__.columns
        if column.name not in {key, "created_at"}
    }
    await session.execute(statement.on_conflict_do_update(index_elements=[key], set_=updates))


async def seed_gray_harbor(session: AsyncSession) -> None:
    demo = get_gray_harbor_demo_world()
    w = demo.world
    builder = ObservationBuilder()
    observations = builder.build_for_events(
        demo.events,
        demo.characters,
        additional_recipients={"event-day3-guards": ["char-chen-mo"]},
        observation_id_overrides={
            ("event-day1-fever", "char-lin-zhixia"): "obs-lin-fever",
            ("event-day2-north-gate-plan", "char-zhou-qiming"): "obs-zhou-plan",
            ("event-day3-guards", "char-chen-mo"): "obs-chen-rumor",
        },
    )
    observations.extend(
        builder.build_for_oracle(request, response)
        for request in demo.oracleRequests
        for response in demo.oracleResponses
        if response.request_id == request.id
    )
    await _upsert(
        session,
        r.WorldRecord,
        [
            {
                "id": w.id,
                "name": w.name,
                "status": w.status.value,
                "current_time": w.current_time,
                "version": w.version,
                "schema_version": w.schema_version,
                "payload": _payload(w),
            }
        ],
    )
    locations = [
        ("north-market-store", "North Market Store"),
        ("north-market-street", "North Market Street"),
        ("emergency-shelter", "Emergency Shelter"),
        ("north-gate", "North Gate"),
    ]
    await _upsert(
        session,
        r.LocationRecord,
        [
            {
                "id": location_id,
                "world_id": w.id,
                "name": name,
                "schema_version": w.schema_version,
                "payload": {"id": location_id, "world_id": w.id, "name": name},
            }
            for location_id, name in locations
        ],
    )
    edge_rows = [
        ("north-market-store", "north-market-street"),
        ("north-market-street", "north-market-store"),
        ("north-market-street", "emergency-shelter"),
        ("emergency-shelter", "north-market-street"),
        ("north-market-street", "north-gate"),
    ]
    edge_statement = insert(r.LocationEdgeRecord).values(
        [
            {"world_id": w.id, "from_location_id": source, "to_location_id": target}
            for source, target in edge_rows
        ]
    )
    await session.execute(edge_statement.on_conflict_do_nothing())
    witness = Character(
        id="char-market-witness",
        world_id=w.id,
        name="Market Witness",
        description="A local resident at the shared market street.",
        location_id="north-market-street",
        occupation=None,
        age=None,
        status=CharacterStatus.ACTIVE,
        is_special_agent=False,
        health=1.0,
        resources={},
        version=1,
        schema_version=w.schema_version,
        created_at=w.created_at,
        updated_at=w.updated_at,
    )
    await _upsert(
        session,
        r.CharacterRecord,
        [
            {
                "id": x.id,
                "world_id": x.world_id,
                "name": x.name,
                "version": x.version,
                "schema_version": x.schema_version,
                "payload": _payload(x),
            }
            for x in [*demo.characters, witness]
        ],
    )
    await _upsert(
        session,
        r.AgentProfileRecord,
        [
            {
                "character_id": x.character_id,
                "world_id": w.id,
                "schema_version": x.schema_version,
                "payload": _payload(x),
            }
            for x in demo.agentProfiles
        ],
        "character_id",
    )
    fact_specs = [
        (
            "fact-fever-cluster",
            "Harbor fever cases",
            "form",
            "an unusual cluster",
            "restricted",
            "event-day1-fever",
        ),
        (
            "fact-fast-spread",
            "Pathogen transmission",
            "is",
            "faster than expected",
            "secret",
            "event-day1-pathogen",
        ),
        (
            "fact-panic-buying",
            "North market",
            "has",
            "panic buying and shortages",
            "public",
            "event-day2-panic-buying",
        ),
        (
            "fact-north-gate-plan",
            "City hall",
            "approved",
            "a north gate lockdown plan",
            "secret",
            "event-day2-north-gate-plan",
        ),
        (
            "fact-north-gate-guards",
            "North gate",
            "has",
            "additional guards",
            "restricted",
            "event-day3-guards",
        ),
        (
            "fact-chen-delays-north-gate",
            "Chen Mo",
            "decides",
            "to remain in the store",
            "private",
            "event-chen-action-result",
        ),
    ]
    events_by_id = {event.id: event for event in demo.events}
    facts = [
        WorldFact.model_validate(
            {
                "id": fact_id,
                "world_id": w.id,
                "subject": subject,
                "predicate": predicate,
                "object": object_value,
                "valid_from": events_by_id[event_id].occurred_at,
                "valid_until": None,
                "visibility": FactVisibility(visibility),
                "source_event_id": event_id,
                "version": 1,
                "schema_version": "1.0",
                "created_at": events_by_id[event_id].created_at,
            }
        )
        for fact_id, subject, predicate, object_value, visibility, event_id in fact_specs
    ]
    await _upsert(
        session,
        r.WorldFactRecord,
        [
            {
                "id": x.id,
                "world_id": x.world_id,
                "visibility": x.visibility.value,
                "valid_from": x.valid_from,
                "source_event_id": x.source_event_id,
                "version": x.version,
                "schema_version": x.schema_version,
                "payload": _payload(x),
            }
            for x in facts
        ],
    )
    await _upsert(
        session,
        r.WorldEventRecord,
        [
            {
                "id": x.id,
                "world_id": x.world_id,
                "event_type": x.event_type.value,
                "occurred_at": x.occurred_at,
                "visibility": x.visibility.value,
                "correlation_id": x.correlation_id,
                "source_action_id": x.source_action_id,
                "schema_version": x.schema_version,
                "payload": _payload(x),
            }
            for x in demo.events
        ],
    )
    await _upsert(
        session,
        r.ObservationRecord,
        [
            {
                "id": x.id,
                "world_id": x.world_id,
                "agent_id": x.agent_id,
                "observed_at": x.observed_at,
                "source_event_id": x.source_event_id,
                "source_message_id": x.source_message_id,
                "schema_version": x.schema_version,
                "payload": _payload(x),
            }
            for x in observations
        ],
    )
    await _upsert(
        session,
        r.AgentBeliefRecord,
        [
            {
                "id": x.id,
                "world_id": x.world_id,
                "agent_id": x.agent_id,
                "learned_at": x.learned_at,
                "source_id": x.source_id,
                "schema_version": x.schema_version,
                "payload": _payload(x),
            }
            for x in demo.beliefs
        ],
    )
    await _upsert(
        session,
        r.OracleRequestRecord,
        [
            {
                "id": x.id,
                "world_id": x.world_id,
                "agent_id": x.agent_id,
                "requested_at": x.requested_at,
                "decision_correlation_id": x.decision_correlation_id,
                "schema_version": x.schema_version,
                "payload": _payload(x),
            }
            for x in demo.oracleRequests
        ],
    )
    await _upsert(
        session,
        r.OracleResponseRecord,
        [
            {
                "id": x.id,
                "request_id": x.request_id,
                "world_id": x.world_id,
                "agent_id": x.agent_id,
                "responded_at": x.responded_at,
                "schema_version": x.schema_version,
                "payload": _payload(x),
            }
            for x in demo.oracleResponses
        ],
    )
    await _upsert(
        session,
        r.ActionIntentRecord,
        [
            {
                "id": x.id,
                "world_id": x.world_id,
                "actor_id": x.actor_id,
                "submitted_at": x.submitted_at,
                "correlation_id": x.correlation_id,
                "schema_version": x.schema_version,
                "payload": _payload(x),
            }
            for x in demo.actionIntents
        ],
    )
    await _upsert(
        session,
        r.ActionResultRecord,
        [
            {
                "id": x.id,
                "world_id": x.world_id,
                "action_id": x.action_id,
                "actor_id": x.actor_id,
                "started_at": x.started_at,
                "completed_at": x.completed_at,
                "correlation_id": x.correlation_id,
                "schema_version": x.schema_version,
                "payload": _payload(x),
            }
            for x in demo.actionResults
        ],
    )
    await session.commit()


async def main() -> None:
    database = Database(get_settings().database_url)
    try:
        async with database.session_factory() as session:
            await seed_gray_harbor(session)
    finally:
        await database.dispose()


if __name__ == "__main__":
    asyncio.run(main())
