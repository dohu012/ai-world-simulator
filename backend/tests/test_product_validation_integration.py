import asyncio
import os
from time import perf_counter

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError

from app.application.product_validation_service import (
    QUESTION_RULES,
    ProbeInput,
    ProductValidationService,
    ResponseInput,
)
from app.infrastructure.database.product_validation_models import StudyParticipantRecord
from app.infrastructure.database.session import Database

pytestmark = pytest.mark.skipif(os.getenv("RUN_INFRA_TESTS") != "1", reason="requires PostgreSQL")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://simulator:simulator@127.0.0.1:5432/simulator",
)


@pytest.mark.asyncio
async def test_durable_correction_withdrawal_and_deletion_flow() -> None:
    database = Database(DATABASE_URL)
    service = ProductValidationService(database.session_factory, code_pepper="x" * 32)
    access_code, _ = await service.issue_access_code()
    enrolled = await service.enroll(
        access_code=access_code,
        acknowledgement_codes={"fiction", "bounded_data", "withdrawal"},
        device_class="desktop",
    )
    try:
        assert len((await service.state(enrolled.participant_id)).periods) == 2
        assert (await service.presentation(enrolled.participant_id, 1)).claims
        await service.complete_exposure(enrolled.participant_id, 1)
        answer = ResponseInput(question_id="pressure", rating=2)
        response_id = await service.respond(enrolled.participant_id, 1, answer, "response-retry")
        assert response_id == await service.respond(
            enrolled.participant_id, 1, answer, "response-retry"
        )
        correction = ResponseInput(question_id="pressure", rating=1)
        corrected_id = await service.correct(
            enrolled.participant_id, response_id, correction, "correction-retry"
        )
        assert corrected_id == await service.correct(
            enrolled.participant_id, response_id, correction, "correction-retry"
        )
        await service.submit_probe(
            enrolled.participant_id,
            ProbeInput(
                probe_type="return_loop_ux",
                initiated=True,
                completed=True,
                reason_code="first_choice",
                effort_rating=3,
                first_choice_rank=1,
            ),
        )
        for question_id, (_, options) in QUESTION_RULES.items():
            if question_id == "pressure":
                continue
            value = (
                ResponseInput(question_id=question_id, rating=3)
                if not options
                else ResponseInput(question_id=question_id, option_code=sorted(options)[0])
            )
            await service.respond(enrolled.participant_id, 1, value, f"required-{question_id}")
        await service.complete_period(enrolled.participant_id, 1)
        await service.withdraw(enrolled.participant_id)
        assert (
            await service.authenticate(access_code, include_withdrawn=True)
        ).id == enrolled.participant_id
    finally:
        await service.delete_participant(enrolled.participant_id)
        async with database.session_factory() as session:
            assert (
                await session.scalar(
                    select(StudyParticipantRecord).where(
                        StudyParticipantRecord.id == enrolled.participant_id
                    )
                )
                is None
            )
        await database.dispose()


@pytest.mark.asyncio
async def test_duplicate_two_worker_enrollment_is_one_assignment() -> None:
    database = Database(DATABASE_URL)
    service = ProductValidationService(database.session_factory, code_pepper="x" * 32)
    access_code, _ = await service.issue_access_code()
    arguments = {
        "access_code": access_code,
        "acknowledgement_codes": {"fiction", "bounded_data", "withdrawal"},
        "device_class": "desktop",
    }
    left, right = await asyncio.gather(service.enroll(**arguments), service.enroll(**arguments))
    try:
        assert left.participant_id == right.participant_id
        assert left.sequence == right.sequence
    finally:
        await service.delete_participant(left.participant_id)
        await database.dispose()


@pytest.mark.asyncio
async def test_production_code_revocation_interval_and_database_freeze() -> None:
    database = Database(DATABASE_URL)
    service = ProductValidationService(database.session_factory, code_pepper="y" * 32)
    access_code, _ = await service.issue_access_code()
    enrolled = await service.enroll(
        access_code=access_code,
        acknowledgement_codes={"fiction", "bounded_data", "withdrawal"},
        device_class="unknown",
    )
    try:
        with pytest.raises(ValueError, match="offline interval"):
            await service.presentation(enrolled.participant_id, 2)
        async with database.session_factory() as session:
            with pytest.raises(DBAPIError, match="immutable"):
                async with session.begin():
                    await session.execute(
                        text(
                            "UPDATE study_questions SET prompt = 'tampered' "
                            "WHERE protocol_id = :protocol_id"
                        ),
                        {"protocol_id": "gray-harbor-product-validation"},
                    )
        await service.revoke_access_code(access_code)
        with pytest.raises(ValueError, match="invalid or expired"):
            await service.authenticate(access_code)
    finally:
        await service.delete_participant(enrolled.participant_id)
        await database.dispose()


@pytest.mark.asyncio
async def test_32_participant_activation_budget_and_cleanup() -> None:
    database = Database(DATABASE_URL)
    service = ProductValidationService(database.session_factory, code_pepper="z" * 32)
    codes = [
        code for code, _ in await asyncio.gather(*(service.issue_access_code() for _ in range(32)))
    ]
    started = perf_counter()
    enrolled = await asyncio.gather(
        *(
            service.enroll(
                access_code=code,
                acknowledgement_codes={"fiction", "bounded_data", "withdrawal"},
                device_class="unknown",
            )
            for code in codes
        )
    )
    elapsed = perf_counter() - started
    try:
        assert len({item.participant_id for item in enrolled}) == 32
        assert elapsed < 10
    finally:
        await asyncio.gather(
            *(service.delete_participant(item.participant_id) for item in enrolled)
        )
        await database.dispose()
