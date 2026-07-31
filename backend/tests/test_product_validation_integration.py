import asyncio
import os
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.application.product_validation_service import (
    QUESTION_RULES,
    ProbeInput,
    ProductValidationService,
    ResponseInput,
)
from app.infrastructure.database.product_validation_models import StudyParticipantRecord
from app.infrastructure.database.session import Database

pytestmark = pytest.mark.skipif(os.getenv("RUN_INFRA_TESTS") != "1", reason="requires PostgreSQL")
DATABASE_URL = "postgresql+asyncpg://simulator:simulator@127.0.0.1:5432/simulator"


@pytest.mark.asyncio
async def test_durable_correction_withdrawal_and_deletion_flow() -> None:
    database = Database(DATABASE_URL)
    service = ProductValidationService(database.session_factory)
    access_code = f"task23-flow-{uuid4().hex}"
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
    service = ProductValidationService(database.session_factory)
    access_code = f"task23-race-{uuid4().hex}"
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
