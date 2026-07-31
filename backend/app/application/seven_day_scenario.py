"""Deterministic read model and bounded coordinator for Gray Harbor scenario v1."""

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.gray_harbor import WORLD_ID
from app.domain.enums import ActionType
from app.domain.seven_day import adjudicate
from app.infrastructure.database import evolution_models as er
from app.infrastructure.database import models as r
from app.infrastructure.database import return_loop_models as return_db
from app.infrastructure.database import runtime_models as rr
from app.infrastructure.database import seven_day_models as sr
from app.infrastructure.database.seven_day_models import ScenarioCheckpointRecord

SCENARIO = Path(__file__).parents[1] / "scenarios" / "gray_harbor_seven_day_v1.json"


class ScenarioAction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    day: int
    actor_id: str
    action_type: ActionType
    status: str
    consequence: str
    failure_code: str | None = None


class ScenarioPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    owner_id: str
    objective: str
    status: str
    blockage_code: str | None = None


class SevenDayScenarioRead(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str
    current_day: int = Field(ge=0, le=7)
    status: str
    residents: list[dict[str, object]]
    resources: dict[str, int]
    capacities: dict[str, int]
    events: list[dict[str, object]]
    plans: list[ScenarioPlan]
    actions: list[ScenarioAction]
    outcomes: list[str]
    model_calls: int


_ACTIONS = (
    ScenarioAction(
        day=1,
        actor_id="char-lin-zhixia",
        action_type=ActionType.CONSUME_RESOURCE,
        status="succeeded",
        consequence="One medicine dose treats Aunt Qiao.",
    ),
    ScenarioAction(
        day=2,
        actor_id="char-chen-mo",
        action_type=ActionType.TRANSFER_RESOURCE,
        status="succeeded",
        consequence="Chen gives four food rations to the Sun household.",
    ),
    ScenarioAction(
        day=3,
        actor_id="char-zhou-qiming",
        action_type=ActionType.QUEUE_FOR_SERVICE,
        status="succeeded",
        consequence="Zhou registers the official checkpoint roster.",
    ),
    ScenarioAction(
        day=4,
        actor_id="char-lin-zhixia",
        action_type=ActionType.ACQUIRE_RESOURCE,
        status="rejected",
        consequence="The hidden cache is not an offered account.",
        failure_code="ACTION_TARGET_NOT_ALLOWED",
    ),
    ScenarioAction(
        day=5,
        actor_id="char-chen-mo",
        action_type=ActionType.HELP_CHARACTER,
        status="succeeded",
        consequence="Chen spends time and two rations helping Luo Min.",
    ),
    ScenarioAction(
        day=6,
        actor_id="char-zhou-qiming",
        action_type=ActionType.ATTEMPT_ROUTE,
        status="succeeded",
        consequence="Zhou clears the risky clinic route.",
    ),
    ScenarioAction(
        day=6,
        actor_id="char-lin-zhixia",
        action_type=ActionType.HELP_CHARACTER,
        status="succeeded",
        consequence="Lin completes the bounded triage plan.",
    ),
    ScenarioAction(
        day=6,
        actor_id="char-chen-mo",
        action_type=ActionType.ABANDON_PLAN,
        status="succeeded",
        consequence="Chen abandons the blocked store replenishment plan.",
    ),
    ScenarioAction(
        day=7,
        actor_id="char-zhou-qiming",
        action_type=ActionType.QUEUE_FOR_SERVICE,
        status="succeeded",
        consequence="Zhou irreversibly allocates all ten rescue seats.",
    ),
)

_DAILY_AFFORDANCES: dict[int, tuple[tuple[str, ActionType, str], ...]] = {
    1: (("char-lin-zhixia", ActionType.CONSUME_RESOURCE, "gh-v1:consume-medicine"),),
    2: (("char-chen-mo", ActionType.TRANSFER_RESOURCE, "gh-v1:transfer-food"),),
    3: (("char-zhou-qiming", ActionType.QUEUE_FOR_SERVICE, "gh-v1:queue-checkpoint"),),
    4: (("char-lin-zhixia", ActionType.ACQUIRE_RESOURCE, "gh-v1:acquire-hidden-cache"),),
    5: (("char-chen-mo", ActionType.HELP_CHARACTER, "gh-v1:help-luo"),),
    6: (
        ("char-lin-zhixia", ActionType.HELP_CHARACTER, "gh-v1:complete-triage"),
        ("char-zhou-qiming", ActionType.ATTEMPT_ROUTE, "gh-v1:route-clinic"),
        ("char-chen-mo", ActionType.ABANDON_PLAN, "gh-v1:abandon-store-plan"),
    ),
    7: (("char-zhou-qiming", ActionType.QUEUE_FOR_SERVICE, "gh-v1:allocate-rescue-seats"),),
}


def daily_affordances(day: int) -> tuple[tuple[str, ActionType, str], ...]:
    return _DAILY_AFFORDANCES.get(day, ())


def build_scenario(day: int) -> SevenDayScenarioRead:
    if not 0 <= day <= 7:
        raise ValueError("day must be between zero and seven")
    fixture = json.loads(SCENARIO.read_text(encoding="utf-8"))
    resources = {"food": 90, "water": 120, "medicine": 8}
    daily_food = (0, 6, 18, 12, 14, 16, 12, 8)
    for current in range(1, day + 1):
        resources["food"] = max(0, resources["food"] - daily_food[current])
        resources["water"] = max(0, resources["water"] - 10)
        if current in {1, 4, 6}:
            resources["medicine"] = max(0, resources["medicine"] - 1)
    actions = [action for action in _ACTIONS if action.day <= day]
    plans = [
        ScenarioPlan(
            owner_id="char-lin-zhixia",
            objective="Triage and stabilize patients",
            status="completed" if day >= 6 else "active",
        ),
        ScenarioPlan(
            owner_id="char-zhou-qiming",
            objective="Maintain checkpoint and rescue access",
            status="completed" if day >= 7 else "active",
        ),
        ScenarioPlan(
            owner_id="char-chen-mo",
            objective="Replenish and protect household supplies",
            status="abandoned" if day >= 6 else ("blocked" if day >= 5 else "active"),
            blockage_code="SHIPMENT_STOPPED" if day >= 5 else None,
        ),
    ]
    outcomes: list[str] = []
    if day >= 7:
        trace = adjudicate(
            world_id="world-gray-harbor",
            scenario_version="1.0.0",
            idempotency_key="day-7-rescue-branch",
            policy_id="rescue-route-v1",
            policy_version=1,
            attempt=1,
            threshold_basis_points=6500,
        )
        outcomes = [
            "Ten rescue seats are irreversibly allocated.",
            "Lin remains with two critical patients.",
            "Zhou escorts the selected residents.",
            (
                f"Chen's route roll is {trace.roll_basis_points}; "
                f"outcome={'success' if trace.accepted else 'failure'}."
            ),
        ]
    return SevenDayScenarioRead(
        version=fixture["version"],
        current_day=day,
        status="completed" if day == 7 else ("ready" if day == 0 else "running"),
        residents=fixture["residents"],
        resources=resources,
        capacities=fixture["capacities"],
        events=[event for event in fixture["days"] if event["day"] <= day],
        plans=plans,
        actions=actions,
        outcomes=outcomes,
        model_calls=0,
    )


class SevenDayScenarioService:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self.sessions = sessions

    async def read(self) -> SevenDayScenarioRead:
        async with self.sessions() as session:
            checkpoint = await session.get(ScenarioCheckpointRecord, WORLD_ID)
            return build_scenario(checkpoint.current_day if checkpoint else 0)

    async def reset(self) -> SevenDayScenarioRead:
        async with self.sessions.begin() as session:
            await self._seed_authoritative_state(session)
            await session.execute(delete(return_db.PlaytestEventRecord))
            await session.execute(delete(return_db.InboxItemRecord))
            await session.execute(delete(return_db.OfflineSummaryClaimRecord))
            await session.execute(delete(return_db.OfflineSummaryRecord))
            await session.execute(delete(return_db.OfflineIntervalRecord))
            await session.execute(delete(return_db.NotificationPreferenceRecord))
            await session.execute(delete(er.evolution_evidence_links))
            await session.execute(delete(er.evolution_deltas))
            await session.execute(delete(er.reflection_jobs))
            await session.execute(delete(er.relationship_snapshots))
            await session.execute(delete(er.identity_snapshots))
            await session.execute(delete(er.identity_baselines))
            world = await session.get(r.WorldRecord, WORLD_ID)
            if world is None:
                raise ValueError("SCENARIO_NOT_INITIALIZED")
            existing_checkpoint = await session.get(
                ScenarioCheckpointRecord, WORLD_ID, with_for_update=True
            )
            prior_generation = 0
            if existing_checkpoint is not None:
                value = existing_checkpoint.payload.get("reset_generation")
                if isinstance(value, int):
                    prior_generation = value
            historical_payloads = (
                await session.scalars(select(r.ActionIntentRecord.payload))
            ).all()
            for payload in historical_payloads:
                idempotency_key = payload.get("idempotency_key")
                key_match = (
                    re.match(r"scenario-g(\d+)-", idempotency_key)
                    if isinstance(idempotency_key, str)
                    else None
                )
                if key_match is not None:
                    prior_generation = max(prior_generation, int(key_match.group(1)))
                summary = payload.get("reason_summary")
                if not isinstance(summary, str):
                    continue
                match = re.fullmatch(
                    r"Execute the current server-offered scenario step for generation (\d+)\.",
                    summary,
                )
                if match is not None:
                    prior_generation = max(prior_generation, int(match.group(1)))
            checkpoint_payload = {
                "reset_reason": "demo_explicit",
                "started_world_time": world.current_time.isoformat(),
                "reset_generation": prior_generation + 1,
            }
            condition_values = {
                "world_id": WORLD_ID,
                "idempotency_key": (f"scenario-v1-g{prior_generation + 1}-day5-shipment-stop"),
                "status": "pending",
                "deadline_world_time": world.current_time + timedelta(days=5),
                "fired_at": None,
                "payload": {
                    "condition": {"field": "day", "op": "gte", "value": 5},
                    "event_type": "food_shipment_stopped",
                    "reset_generation": prior_generation + 1,
                },
            }
            condition_statement = insert(sr.ConditionalEventRecord).values(
                id="condition-food-shipment-stop", **condition_values
            )
            await session.execute(
                condition_statement.on_conflict_do_update(
                    index_elements=["id"], set_=condition_values
                )
            )
            runtime = await session.get(rr.WorldRuntimeRecord, WORLD_ID, with_for_update=True)
            if runtime is not None:
                runtime.current_world_time = world.current_time
                runtime.status = "stopped"
                runtime.generation += 1
                runtime.version += 1
            statement = insert(ScenarioCheckpointRecord).values(
                world_id=WORLD_ID,
                scenario_version="1.0.0",
                current_day=0,
                status="ready",
                version=1,
                payload=checkpoint_payload,
            )
            statement = statement.on_conflict_do_update(
                index_elements=[ScenarioCheckpointRecord.world_id],
                set_={
                    "scenario_version": "1.0.0",
                    "current_day": 0,
                    "status": "ready",
                    "version": ScenarioCheckpointRecord.version + 1,
                    "payload": checkpoint_payload,
                },
            )
            await session.execute(statement)
        return build_scenario(0)

    @staticmethod
    async def _seed_authoritative_state(session: AsyncSession) -> None:
        fixture = json.loads(SCENARIO.read_text(encoding="utf-8"))
        for tier, due_minute, priority in (
            ("L0", 480, 400),
            ("L1", 450, 300),
            ("L2", 420, 200),
            ("L3", 390, 100),
        ):
            identifier = f"schedule-{tier.lower()}-daily-v1"
            values = {
                "world_id": WORLD_ID,
                "tier": tier,
                "due_minute": due_minute,
                "priority": priority,
                "version": 1,
                "payload": {"kind": "daily_demand", "model_calls": 0},
            }
            statement = insert(sr.ScheduleTemplateRecord).values(id=identifier, **values)
            await session.execute(
                statement.on_conflict_do_update(index_elements=["id"], set_=values)
            )
        for resident in fixture["residents"]:
            identifier = str(resident["id"])
            tier = str(resident["tier"])
            values = {
                "world_id": WORLD_ID,
                "tier": tier,
                "role": str(resident["role"]),
                "location_id": str(resident["location"]),
                "status": "active",
                "schedule_template_id": f"schedule-{tier.lower()}-daily-v1",
                "version": 1,
                "payload": resident,
            }
            statement = insert(sr.ResidentSimulationRecord).values(id=identifier, **values)
            await session.execute(
                statement.on_conflict_do_update(index_elements=["id"], set_=values)
            )
        definitions = (
            ("resource-food", "food", "ration"),
            ("resource-water", "water", "litre"),
            ("resource-medicine", "medicine", "dose"),
            ("resource-rescue-seat", "rescue_seat", "seat"),
        )
        for identifier, resource_type, unit in definitions:
            statement = insert(sr.ResourceDefinitionRecord).values(
                id=identifier,
                world_id=WORLD_ID,
                resource_type=resource_type,
                unit=unit,
                version=1,
                payload={"id": identifier, "resource_type": resource_type, "unit": unit},
            )
            await session.execute(statement.on_conflict_do_nothing(index_elements=["id"]))
        accounts = (
            ("account-store-food", "resource-food", "location", "store", 90, 120),
            ("account-sun-food", "resource-food", "household", "sun", 0, 30),
            ("account-luo-food", "resource-food", "character", "resident-11", 0, 30),
            ("account-clinic-medicine", "resource-medicine", "location", "clinic", 8, 20),
            (
                "account-rescue-seats",
                "resource-rescue-seat",
                "service",
                "rescue",
                10,
                10,
            ),
        )
        for identifier, resource_id, holder_kind, holder_id, available, capacity in accounts:
            values = {
                "world_id": WORLD_ID,
                "resource_id": resource_id,
                "holder_kind": holder_kind,
                "holder_id": holder_id,
                "available": available,
                "reserved": 0,
                "consumed": 0,
                "capacity": capacity,
                "version": 1,
                "payload": {
                    "id": identifier,
                    "available": available,
                    "reserved": 0,
                    "consumed": 0,
                    "version": 1,
                },
            }
            statement = insert(sr.ResourceAccountRecord).values(id=identifier, **values)
            await session.execute(
                statement.on_conflict_do_update(
                    index_elements=["id"],
                    set_=values,
                )
            )
        deadline = datetime(2026, 8, 4, tzinfo=UTC)
        goals = (
            ("goal-lin-triage", "char-lin-zhixia", 90),
            ("goal-zhou-rescue", "char-zhou-qiming", 85),
            ("goal-chen-supplies", "char-chen-mo", 80),
        )
        for identifier, owner_id, priority in goals:
            values = {
                "world_id": WORLD_ID,
                "owner_id": owner_id,
                "status": "active",
                "priority": priority,
                "version": 1,
                "payload": {"id": identifier, "owner_id": owner_id, "status": "active"},
            }
            statement = insert(sr.AgentGoalRecord).values(id=identifier, **values)
            await session.execute(
                statement.on_conflict_do_update(index_elements=["id"], set_=values)
            )
        plans = (
            ("plan-lin-triage", "char-lin-zhixia", "goal-lin-triage"),
            ("plan-zhou-rescue", "char-zhou-qiming", "goal-zhou-rescue"),
            ("plan-chen-supplies", "char-chen-mo", "goal-chen-supplies"),
        )
        for identifier, owner_id, goal_id in plans:
            values = {
                "world_id": WORLD_ID,
                "owner_id": owner_id,
                "goal_id": goal_id,
                "slot": "primary",
                "status": "active",
                "deadline_world_time": deadline,
                "replan_count": 0,
                "retry_count": 0,
                "version": 1,
                "fencing_token": 1,
                "payload": {"id": identifier, "owner_id": owner_id, "status": "active"},
            }
            statement = insert(sr.AgentPlanRecord).values(id=identifier, **values)
            await session.execute(
                statement.on_conflict_do_update(index_elements=["id"], set_=values)
            )
