import os
from asyncio import gather

import pytest
from sqlalchemy import delete, func, select

from app.application.action_lifecycle import DemoActionSubmission, GrayHarborActionService
from app.application.runtime_service import AdvanceCommand, PostgresWorldRuntimeAdapter
from app.application.seven_day_scenario import SevenDayScenarioService
from app.core.config import Settings
from app.domain.enums import ActionStatus, ActionType
from app.infrastructure.database import models as r
from app.infrastructure.database import seven_day_models as sr
from app.infrastructure.database.session import Database
from app.repositories.worlds import WorldRepository
from app.services.seed_gray_harbor import seed_gray_harbor

pytestmark = pytest.mark.skipif(os.getenv("RUN_INFRA_TESTS") != "1", reason="requires PostgreSQL")


async def test_resource_transfer_is_atomic_conserved_and_idempotent() -> None:
    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as session:
            await seed_gray_harbor(session)
        scenario = SevenDayScenarioService(database.session_factory)
        await scenario.reset()
        async with database.session_factory() as session:
            intent_id = "intent-demo-23fe8aa288de8504e5ec"
            event_id = "event-demo-23fe8aa288de8504e5ec"
            await session.execute(
                delete(sr.ResourceLedgerRecord).where(
                    sr.ResourceLedgerRecord.id.like(f"ledger-{intent_id}-%")
                )
            )
            await session.execute(
                delete(r.ObservationRecord).where(r.ObservationRecord.source_event_id == event_id)
            )
            await session.execute(
                delete(r.WorldEventRecord).where(r.WorldEventRecord.id == event_id)
            )
            await session.execute(
                delete(r.ActionResultRecord).where(r.ActionResultRecord.action_id == intent_id)
            )
            await session.execute(
                delete(r.ActionIntentRecord).where(r.ActionIntentRecord.id == intent_id)
            )
            await session.commit()
        submission = DemoActionSubmission(
            idempotency_key="task019-transfer-proof",
            action_type=ActionType.TRANSFER_RESOURCE,
            parameters={"affordance_id": "gh-v1:transfer-food"},
            reason_summary="Give the offered household ration allocation.",
        )
        async with database.session_factory() as session:
            service = GrayHarborActionService(WorldRepository(session))
            first = await service.submit("char-chen-mo", submission)
            assert first.result.status is ActionStatus.SUCCEEDED
        async with database.session_factory() as session:
            store = await session.get(sr.ResourceAccountRecord, "account-store-food")
            household = await session.get(sr.ResourceAccountRecord, "account-sun-food")
            assert store is not None and household is not None
            assert store.available == 86
            assert household.available == 4
            assert store.available + household.available == 90
            assert (
                await session.scalar(
                    select(func.count())
                    .select_from(sr.ResourceLedgerRecord)
                    .where(sr.ResourceLedgerRecord.id.like(f"ledger-{intent_id}-%"))
                )
                == 2
            )
            replay = await GrayHarborActionService(WorldRepository(session)).submit(
                "char-chen-mo", submission
            )
            assert replay.idempotent_replay is True
            store = await session.get(sr.ResourceAccountRecord, "account-store-food")
            assert store is not None and store.available == 86
    finally:
        await database.dispose()


async def test_only_existing_runtime_advance_moves_scenario_day() -> None:
    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as session:
            await seed_gray_harbor(session)
        scenario = SevenDayScenarioService(database.session_factory)
        assert (await scenario.reset()).current_day == 0
        async with database.session_factory() as session:
            assert (
                await session.scalar(select(func.count()).select_from(sr.ResidentSimulationRecord))
                == 30
            )
            assert (
                await session.scalar(
                    select(func.count())
                    .select_from(sr.ResidentSimulationRecord)
                    .where(sr.ResidentSimulationRecord.tier == "L3")
                )
                == 3
            )
            assert (
                await session.scalar(select(func.count()).select_from(sr.ScheduleTemplateRecord))
                == 4
            )
            checkpoint = await session.get(
                sr.ScenarioCheckpointRecord, "world-gray-harbor-lockdown"
            )
            assert checkpoint is not None
            scenario_generation = checkpoint.payload["reset_generation"]
            assert isinstance(scenario_generation, int)
        runtime = PostgresWorldRuntimeAdapter(database.session_factory, enabled=True)
        current = await runtime.start()
        for day in range(1, 8):
            if day == 4:
                runtime = PostgresWorldRuntimeAdapter(database.session_factory, enabled=True)
            current = await runtime.advance(
                AdvanceCommand(minutes=1440, expected_generation=current.generation)
            )
            state = await SevenDayScenarioService(database.session_factory).read()
            assert state.current_day == day
            assert state.model_calls == 0
        completed = await scenario.read()
        assert completed.status == "completed"
        assert len(completed.outcomes) == 4
        async with database.session_factory() as session:
            rejected = await GrayHarborActionService(WorldRepository(session)).submit(
                "char-zhou-qiming",
                DemoActionSubmission(
                    idempotency_key="task019-final-seat-loser",
                    action_type=ActionType.QUEUE_FOR_SERVICE,
                    parameters={"affordance_id": "gh-v1:allocate-rescue-seats"},
                    reason_summary="Attempt a second allocation after capacity is exhausted.",
                ),
            )
            assert rejected.result.status is ActionStatus.REJECTED
            assert rejected.result.failure_code == "RESOURCE_INSUFFICIENT"
        async with database.session_factory() as session:
            assert (
                await session.scalar(
                    select(func.count())
                    .select_from(r.ActionIntentRecord)
                    .where(
                        r.ActionIntentRecord.payload["reason_summary"].astext
                        == (
                            "Execute the current server-offered scenario step "
                            f"for generation {scenario_generation}."
                        )
                    )
                )
                == 9
            )
            store = await session.get(sr.ResourceAccountRecord, "account-store-food")
            medicine = await session.get(sr.ResourceAccountRecord, "account-clinic-medicine")
            plan = await session.get(sr.AgentPlanRecord, "plan-chen-supplies")
            lin_plan = await session.get(sr.AgentPlanRecord, "plan-lin-triage")
            zhou_plan = await session.get(sr.AgentPlanRecord, "plan-zhou-rescue")
            rescue = await session.get(sr.ResourceAccountRecord, "account-rescue-seats")
            condition = await session.get(sr.ConditionalEventRecord, "condition-food-shipment-stop")
            assert store is not None and store.available == 84
            assert medicine is not None and medicine.available == 7
            assert plan is not None and plan.status == "abandoned"
            assert lin_plan is not None and lin_plan.status == "completed"
            assert zhou_plan is not None and zhou_plan.status == "completed"
            assert rescue is not None and rescue.available == 0
            assert rescue.consumed == 10
            assert condition is not None and condition.status == "fired"
            event_id = condition.payload["event_id"]
            assert isinstance(event_id, str)
            assert (
                await session.scalar(
                    select(func.count())
                    .select_from(r.WorldEventRecord)
                    .where(r.WorldEventRecord.id == event_id)
                )
                == 1
            )
    finally:
        await database.dispose()


async def test_two_workers_race_for_final_rescue_capacity() -> None:
    database = Database(Settings().database_url)
    try:
        async with database.session_factory() as session:
            await seed_gray_harbor(session)
        scenario = SevenDayScenarioService(database.session_factory)
        await scenario.reset()
        async with database.session_factory() as session:
            checkpoint = await session.get(
                sr.ScenarioCheckpointRecord, "world-gray-harbor-lockdown"
            )
            assert checkpoint is not None
            generation = checkpoint.payload["reset_generation"]
            assert isinstance(generation, int)

        async def submit(worker: str) -> ActionStatus:
            async with database.session_factory() as session:
                result = await GrayHarborActionService(WorldRepository(session)).submit(
                    "char-zhou-qiming",
                    DemoActionSubmission(
                        idempotency_key=f"scenario-g{generation}-seat-race-{worker}",
                        action_type=ActionType.QUEUE_FOR_SERVICE,
                        parameters={"affordance_id": "gh-v1:allocate-rescue-seats"},
                        reason_summary="Compete for the final offered rescue capacity.",
                    ),
                )
                return result.result.status

        statuses = await gather(submit("a"), submit("b"))
        assert sorted(status.value for status in statuses) == ["rejected", "succeeded"]
        async with database.session_factory() as session:
            rescue = await session.get(sr.ResourceAccountRecord, "account-rescue-seats")
            assert rescue is not None
            assert rescue.available == 0
            assert rescue.consumed == 10
    finally:
        await database.dispose()
