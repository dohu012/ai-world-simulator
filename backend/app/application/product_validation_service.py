"""Durable, isolated TASK-023 playtest workflow."""

from __future__ import annotations

import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Literal, cast
from uuid import uuid4

from pydantic import BaseModel, Field
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.product_validation import (
    ASSIGNMENT_VERSION,
    PROTOCOL_ID,
    PROTOCOL_VERSION,
    Presentation,
    PresentationClaim,
    assignment_for,
    protocol_hash,
)
from app.infrastructure.database.product_validation_models import (
    StudyAccessCodeRecord,
    StudyConsentRecord,
    StudyDeletionTombstoneRecord,
    StudyDemandProbeRecord,
    StudyParticipantRecord,
    StudyPeriodRecord,
    StudyProtocolRecord,
    StudyQuestionRecord,
    StudyResponseRecord,
)

CORPUS_PATH = (
    Path(__file__).resolve().parents[1] / "scenarios" / "gray_harbor_product_validation_v1.json"
)
CONSENT_VERSION = "1.0.0"
CONSENT_WORDING = (
    "I consent to a fictional presentation study using an opaque code and bounded answers. "
    "I may withdraw and delete my row-level study data."
)
ALLOWED_ACKNOWLEDGEMENTS = frozenset({"fiction", "bounded_data", "withdrawal"})
QUESTION_RULES: dict[str, tuple[Literal["option", "rating"], frozenset[str]]] = {
    "source": ("option", frozenset({"observation", "oracle", "outcome", "unknown"})),
    "epistemic": ("option", frozenset({"fact", "belief", "decision", "outcome"})),
    "causal_order": ("option", frozenset({"correct", "incorrect", "uncertain"})),
    "pressure": ("rating", frozenset()),
    "anxiety": ("rating", frozenset()),
    "manipulation": ("rating", frozenset()),
    "fictional_intensity": ("rating", frozenset()),
    "clarity": ("rating", frozenset()),
    "usefulness": ("rating", frozenset()),
    "fictional_framing": ("rating", frozenset()),
    "continued_interest": ("option", frozenset({"yes", "no", "unsure"})),
}
QUESTION_WORDING: dict[str, tuple[str, str]] = {
    "source": ("comprehension", "Which authorized source best supports the decision?"),
    "epistemic": (
        "comprehension",
        "Was the selected statement a fact, belief, decision, or outcome?",
    ),
    "causal_order": ("comprehension", "Does this order correctly explain why the character acted?"),
    "pressure": ("participant", "How much pressure was caused to you by this summary/interface?"),
    "anxiety": ("participant", "How much anxiety was caused to you by this summary/interface?"),
    "manipulation": (
        "participant",
        "How manipulated did this summary/interface cause you to feel?",
    ),
    "fictional_intensity": (
        "fictional_world",
        "Separately, how intense was the fictional situation?",
    ),
    "clarity": ("participant", "How clear was this summary/interface to you?"),
    "usefulness": ("participant", "How useful was this summary/interface to you?"),
    "fictional_framing": ("participant", "How clear was it that this was a fictional world?"),
    "continued_interest": ("participant", "Would you choose to follow this character again?"),
}
PROBE_TYPES = frozenset(
    {"creation", "promotion", "dialogue", "actions", "return_loop_ux", "delivery"}
)
Sequence = Literal["AB", "BA"]
EpistemicClass = Literal[
    "objective", "observed", "believed", "correction", "decision", "outcome", "relationship"
]


class EnrollmentResult(BaseModel):
    participant_id: str
    sequence: Literal["AB", "BA"]
    assignment_version: str
    next_period: int


class ParticipantState(BaseModel):
    participant_id: str
    sequence: Literal["AB", "BA"]
    withdrawn: bool
    periods: list[dict[str, object]]


class AggregateState(BaseModel):
    protocol_id: str
    protocol_version: str
    enrolled: int
    completed_both_periods: int
    withdrawn: int
    evidence_class: Literal["directional", "exploratory", "primary"]
    small_cells: Literal["suppressed"]
    decision: Literal["defer"]
    reasons: list[str]


class ResponseInput(BaseModel):
    question_id: str = Field(min_length=1, max_length=96)
    option_code: str | None = Field(default=None, max_length=32)
    rating: int | None = Field(default=None, ge=1, le=5)


class ProbeInput(BaseModel):
    probe_type: str = Field(min_length=1, max_length=32)
    initiated: bool
    completed: bool
    reason_code: str = Field(min_length=1, max_length=32)
    effort_rating: int = Field(ge=1, le=5)
    first_choice_rank: int = Field(ge=1, le=6)


def _hash(*parts: str) -> str:
    return sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def _code_hash(pepper: str, access_code: str) -> str:
    return hmac.new(pepper.encode(), access_code.encode(), sha256).hexdigest()


def _advisory_key(value: str) -> int:
    key = int(value[:16], 16)
    return key if key < 2**63 else key - 2**64


def _corpus() -> dict[str, object]:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def frozen_protocol() -> dict[str, object]:
    corpus = _corpus()
    payload = {
        "id": PROTOCOL_ID,
        "version": PROTOCOL_VERSION,
        "consent_version": CONSENT_VERSION,
        "consent_wording": CONSENT_WORDING,
        "acknowledgement_codes": sorted(ALLOWED_ACKNOWLEDGEMENTS),
        "target": 16,
        "minimum": 8,
        "conditions": ["causal", "chronological"],
        "interval_ids": [item["id"] for item in cast(list[dict[str, object]], corpus["intervals"])],
        "assignment_version": ASSIGNMENT_VERSION,
        "free_text_collected": False,
        "notification_required": False,
    }
    payload["content_hash"] = protocol_hash(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )
    return payload


class ProductValidationService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        *,
        code_pepper: str | None = None,
        min_return_hours: int = 24,
    ) -> None:
        self._session_factory = session_factory
        self._code_pepper = code_pepper
        self._min_return = timedelta(hours=min_return_hours)

    def _require_pepper(self) -> str:
        if not self._code_pepper or len(self._code_pepper) < 32:
            raise ValueError("study access is unavailable")
        return self._code_pepper

    async def issue_access_code(self, *, ttl_hours: int = 168) -> tuple[str, datetime]:
        if ttl_hours < 1 or ttl_hours > 720:
            raise ValueError("access code lifetime is outside the allowed range")
        raw_code = secrets.token_urlsafe(24)
        now = datetime.now(UTC)
        expires_at = now + timedelta(hours=ttl_hours)
        async with self._session_factory() as session, session.begin():
            await self.ensure_protocol(session)
            session.add(
                StudyAccessCodeRecord(
                    id=f"code-{uuid4().hex}",
                    protocol_id=PROTOCOL_ID,
                    code_hash=_code_hash(self._require_pepper(), raw_code),
                    hash_version="hmac-sha256-v1",
                    issued_at=now,
                    expires_at=expires_at,
                )
            )
        return raw_code, expires_at

    async def revoke_access_code(self, access_code: str) -> None:
        code_hash = _code_hash(self._require_pepper(), access_code)
        async with self._session_factory() as session, session.begin():
            issued = await session.scalar(
                select(StudyAccessCodeRecord)
                .where(
                    StudyAccessCodeRecord.protocol_id == PROTOCOL_ID,
                    StudyAccessCodeRecord.code_hash == code_hash,
                )
                .with_for_update()
            )
            if issued:
                issued.revoked_at = issued.revoked_at or datetime.now(UTC)

    async def ensure_protocol(self, session: AsyncSession) -> StudyProtocolRecord:
        existing = await session.get(StudyProtocolRecord, PROTOCOL_ID)
        if existing:
            return existing
        frozen = frozen_protocol()
        record = StudyProtocolRecord(
            id=PROTOCOL_ID,
            version=PROTOCOL_VERSION,
            content_hash=str(frozen["content_hash"]),
            locale="en",
            sample_target=16,
            frozen_at=datetime(2026, 7, 30, tzinfo=UTC),
        )
        session.add(record)
        await session.flush()
        for question_id, (scope, prompt) in QUESTION_WORDING.items():
            kind, options = QUESTION_RULES[question_id]
            session.add(
                StudyQuestionRecord(
                    id=question_id,
                    protocol_id=PROTOCOL_ID,
                    version="1.0.0",
                    construct_code=question_id,
                    scope=scope,
                    prompt=prompt,
                    option_codes="1,2,3,4,5" if kind == "rating" else ",".join(sorted(options)),
                    correct_code=None,
                    wording_hash=_hash(prompt),
                )
            )
        await session.flush()
        return record

    async def enroll(
        self,
        *,
        access_code: str,
        acknowledgement_codes: set[str],
        device_class: str,
    ) -> EnrollmentResult:
        if not 16 <= len(access_code) <= 128:
            raise ValueError("access code is invalid or expired")
        if acknowledgement_codes != ALLOWED_ACKNOWLEDGEMENTS:
            raise ValueError("all consent acknowledgements are required")
        if device_class not in {"desktop", "mobile", "tablet", "assistive", "unknown"}:
            raise ValueError("unsupported device capability class")
        code_hash = _code_hash(self._require_pepper(), access_code)
        frozen = frozen_protocol()
        async with self._session_factory() as session, session.begin():
            # PostgreSQL transaction locks serialize first protocol creation and
            # duplicate enrollment without retaining a lock after commit.
            await session.execute(
                text("SELECT pg_advisory_xact_lock(:key)"),
                {"key": _advisory_key(_hash("study-protocol", PROTOCOL_ID))},
            )
            protocol = await self.ensure_protocol(session)
            await session.execute(
                text("SELECT pg_advisory_xact_lock(:key)"),
                {"key": _advisory_key(code_hash)},
            )
            issued = await session.scalar(
                select(StudyAccessCodeRecord)
                .where(
                    StudyAccessCodeRecord.protocol_id == PROTOCOL_ID,
                    StudyAccessCodeRecord.code_hash == code_hash,
                )
                .with_for_update()
            )
            now = datetime.now(UTC)
            if not issued or issued.revoked_at or issued.expires_at <= now:
                raise ValueError("access code is invalid or expired")
            existing = await session.scalar(
                select(StudyParticipantRecord).where(
                    StudyParticipantRecord.protocol_id == protocol.id,
                    StudyParticipantRecord.opaque_code_hash == code_hash,
                )
            )
            if existing:
                if existing.withdrawn_at:
                    raise ValueError("access code is invalid or expired")
                return EnrollmentResult(
                    participant_id=existing.id,
                    sequence=cast(Sequence, existing.sequence),
                    assignment_version=ASSIGNMENT_VERSION,
                    next_period=await self._next_period(session, existing.id),
                )
            participant_id = f"study-{uuid4().hex}"
            sequence = assignment_for(participant_id, str(frozen["content_hash"]))
            participant = StudyParticipantRecord(
                id=participant_id,
                protocol_id=protocol.id,
                opaque_code_hash=code_hash,
                sequence=sequence,
                assignment_proof=_hash(
                    ASSIGNMENT_VERSION, str(frozen["content_hash"]), participant_id, sequence
                ),
                device_class=device_class,
            )
            session.add(participant)
            issued.activated_at = issued.activated_at or now
            # These deliberately relationship-free records still require an
            # explicit parent flush so PostgreSQL can enforce the FK ordering.
            await session.flush()
            session.add(
                StudyConsentRecord(
                    id=f"consent-{uuid4().hex}",
                    participant_id=participant_id,
                    version=CONSENT_VERSION,
                    wording_hash=_hash(CONSENT_WORDING),
                    status="accepted",
                    acknowledgement_codes=",".join(sorted(acknowledgement_codes)),
                    recorded_at=datetime.now(UTC),
                )
            )
            protocol.enrollment_started_at = protocol.enrollment_started_at or datetime.now(UTC)
            for period in (1, 2):
                condition = (
                    "causal"
                    if (sequence == "AB" and period == 1) or (sequence == "BA" and period == 2)
                    else "chronological"
                )
                intervals = cast(list[dict[str, object]], _corpus()["intervals"])
                interval = intervals[period - 1]
                source_watermark = self._interval_watermark(interval)
                session.add(
                    StudyPeriodRecord(
                        id=f"period-{uuid4().hex}",
                        protocol_id=protocol.id,
                        participant_id=participant_id,
                        period=period,
                        condition=condition,
                        interval_id=str(interval["id"]),
                        source_watermark=source_watermark,
                        presentation_hash=_hash(
                            PROTOCOL_VERSION, str(interval["id"]), condition, source_watermark
                        ),
                    )
                )
            return EnrollmentResult(
                participant_id=participant_id,
                sequence=sequence,
                assignment_version=ASSIGNMENT_VERSION,
                next_period=1,
            )

    async def authenticate(
        self, access_code: str, *, include_withdrawn: bool = False
    ) -> StudyParticipantRecord:
        if not access_code:
            raise ValueError("access code is invalid or expired")
        code_hash = _code_hash(self._require_pepper(), access_code)
        async with self._session_factory() as session:
            issued = await session.scalar(
                select(StudyAccessCodeRecord).where(
                    StudyAccessCodeRecord.protocol_id == PROTOCOL_ID,
                    StudyAccessCodeRecord.code_hash == code_hash,
                    StudyAccessCodeRecord.revoked_at.is_(None),
                    StudyAccessCodeRecord.expires_at > datetime.now(UTC),
                )
            )
            if not issued:
                raise ValueError("access code is invalid or expired")
            participant = await session.scalar(
                select(StudyParticipantRecord).where(
                    StudyParticipantRecord.protocol_id == PROTOCOL_ID,
                    StudyParticipantRecord.opaque_code_hash == code_hash,
                )
            )
            if not participant or (participant.withdrawn_at and not include_withdrawn):
                raise ValueError("access code is invalid or expired")
            session.expunge(participant)
            return participant

    async def state(self, participant_id: str) -> ParticipantState:
        async with self._session_factory() as session:
            participant = await session.get(StudyParticipantRecord, participant_id)
            if not participant:
                raise ValueError("access code is invalid or expired")
            periods = (
                await session.scalars(
                    select(StudyPeriodRecord)
                    .where(StudyPeriodRecord.participant_id == participant_id)
                    .order_by(StudyPeriodRecord.period)
                )
            ).all()
            return ParticipantState(
                participant_id=participant.id,
                sequence=cast(Sequence, participant.sequence),
                withdrawn=participant.withdrawn_at is not None,
                periods=[
                    {
                        "period": item.period,
                        "condition": item.condition,
                        "exposure_completed": item.exposure_completed_at is not None,
                        "returned": item.returned_at is not None,
                        "completed": item.completed_at is not None,
                    }
                    for item in periods
                ],
            )

    async def aggregate_state(self) -> AggregateState:
        async with self._session_factory() as session:
            participants = (
                await session.scalars(
                    select(StudyParticipantRecord).where(
                        StudyParticipantRecord.protocol_id == PROTOCOL_ID
                    )
                )
            ).all()
            completed = 0
            for participant in participants:
                period_count = len(
                    (
                        await session.scalars(
                            select(StudyPeriodRecord.id).where(
                                StudyPeriodRecord.participant_id == participant.id,
                                StudyPeriodRecord.completed_at.is_not(None),
                            )
                        )
                    ).all()
                )
                completed += period_count == 2
            evidence = (
                "primary" if completed >= 16 else "exploratory" if completed >= 8 else "directional"
            )
            return AggregateState(
                protocol_id=PROTOCOL_ID,
                protocol_version=PROTOCOL_VERSION,
                enrolled=len(participants),
                completed_both_periods=completed,
                withdrawn=sum(item.withdrawn_at is not None for item in participants),
                evidence_class=evidence,
                small_cells="suppressed",
                decision="defer",
                reasons=(
                    ["sample_below_8", "human_branch_analysis_not_frozen"]
                    if completed < 8
                    else ["human_branch_analysis_not_frozen"]
                ),
            )

    async def presentation(self, participant_id: str, period: int) -> Presentation:
        async with self._session_factory() as session:
            record = await self._period(session, participant_id, period)
            if period == 2:
                first = await self._period(session, participant_id, 1)
                if (
                    first.completed_at is None
                    or datetime.now(UTC) < first.completed_at + self._min_return
                ):
                    raise ValueError("the offline interval is not complete")
            interval = self._interval(record.interval_id)
            claims: list[PresentationClaim] = [
                PresentationClaim(
                    id=str(item["id"]),
                    source_id=str(item["source_id"]),
                    source_hash=str(item["source_hash"]),
                    epistemic_class=cast(EpistemicClass, item["epistemic_class"]),
                    text=str(item["text"]),
                    ordinal=index,
                )
                for index, item in enumerate(cast(list[dict[str, object]], interval["claims"]))
            ]
            if record.condition == "causal":
                order = {
                    "objective": 0,
                    "observed": 0,
                    "believed": 1,
                    "correction": 2,
                    "decision": 3,
                    "outcome": 4,
                    "relationship": 5,
                }
                claims.sort(key=lambda item: (order[item.epistemic_class], item.ordinal))
            else:
                claims.sort(key=lambda item: item.ordinal)
            return Presentation(
                interval_id=record.interval_id,
                condition=record.condition,  # type: ignore[arg-type]
                claims=tuple(claims),
            )

    async def complete_exposure(self, participant_id: str, period: int) -> None:
        async with self._session_factory() as session, session.begin():
            record = await self._period(session, participant_id, period, for_update=True)
            if record.exposure_completed_at is None:
                record.exposure_completed_at = datetime.now(UTC)

    async def mark_return(self, participant_id: str, period: int) -> None:
        async with self._session_factory() as session, session.begin():
            record = await self._period(session, participant_id, period, for_update=True)
            if record.exposure_completed_at is None:
                raise ValueError("exposure must be completed before return")
            record.returned_at = record.returned_at or datetime.now(UTC)

    async def respond(
        self,
        participant_id: str,
        period: int,
        response: ResponseInput,
        idempotency_key: str,
    ) -> str:
        self._validate_response(response)
        if not idempotency_key or len(idempotency_key) > 128:
            raise ValueError("Idempotency-Key is required")
        async with self._session_factory() as session, session.begin():
            record = await self._period(session, participant_id, period, for_update=True)
            if record.exposure_completed_at is None:
                raise ValueError("answer cannot be accepted before exposure completion")
            existing = await session.scalar(
                select(StudyResponseRecord).where(
                    StudyResponseRecord.participant_id == participant_id,
                    StudyResponseRecord.idempotency_key == idempotency_key,
                )
            )
            if existing:
                return existing.id
            latest = await session.scalar(
                select(StudyResponseRecord)
                .where(
                    StudyResponseRecord.period_id == record.id,
                    StudyResponseRecord.question_id == response.question_id,
                )
                .order_by(StudyResponseRecord.version.desc())
                .limit(1)
            )
            if latest and not latest.invalidated:
                raise ValueError("use correction endpoint to revise an answer")
            answer = StudyResponseRecord(
                id=f"response-{uuid4().hex}",
                participant_id=participant_id,
                period_id=record.id,
                question_id=response.question_id,
                version=1 if latest is None else latest.version + 1,
                option_code=response.option_code,
                rating=response.rating,
                idempotency_key=idempotency_key,
                invalidated=False,
                recorded_at=datetime.now(UTC),
            )
            session.add(answer)
            return answer.id

    async def correct(
        self,
        participant_id: str,
        response_id: str,
        replacement: ResponseInput,
        idempotency_key: str,
    ) -> str:
        self._validate_response(replacement)
        if not idempotency_key or len(idempotency_key) > 128:
            raise ValueError("Idempotency-Key is required")
        async with self._session_factory() as session, session.begin():
            existing = await session.scalar(
                select(StudyResponseRecord).where(
                    StudyResponseRecord.participant_id == participant_id,
                    StudyResponseRecord.idempotency_key == idempotency_key,
                )
            )
            if existing:
                return existing.id
            prior = await session.scalar(
                select(StudyResponseRecord)
                .where(
                    StudyResponseRecord.id == response_id,
                    StudyResponseRecord.participant_id == participant_id,
                )
                .with_for_update()
            )
            if not prior or prior.invalidated:
                raise ValueError("answer is unavailable")
            if replacement.question_id != prior.question_id:
                raise ValueError("correction question must match")
            prior.invalidated = True
            corrected = StudyResponseRecord(
                id=f"response-{uuid4().hex}",
                participant_id=participant_id,
                period_id=prior.period_id,
                question_id=prior.question_id,
                version=prior.version + 1,
                option_code=replacement.option_code,
                rating=replacement.rating,
                idempotency_key=idempotency_key,
                corrects_response_id=prior.id,
                invalidated=False,
                recorded_at=datetime.now(UTC),
            )
            session.add(corrected)
            return corrected.id

    async def submit_probe(self, participant_id: str, value: ProbeInput) -> None:
        if value.probe_type not in PROBE_TYPES:
            raise ValueError("undeclared demand probe")
        async with self._session_factory() as session, session.begin():
            existing = await session.scalar(
                select(StudyDemandProbeRecord).where(
                    StudyDemandProbeRecord.participant_id == participant_id,
                    StudyDemandProbeRecord.probe_type == value.probe_type,
                )
            )
            if existing:
                return
            session.add(
                StudyDemandProbeRecord(
                    id=f"probe-{uuid4().hex}",
                    participant_id=participant_id,
                    **value.model_dump(),
                )
            )

    async def complete_period(self, participant_id: str, period: int) -> None:
        async with self._session_factory() as session, session.begin():
            record = await self._period(session, participant_id, period, for_update=True)
            if record.exposure_completed_at is None:
                raise ValueError("exposure is incomplete")
            question_ids = set(
                (
                    await session.scalars(
                        select(StudyResponseRecord.question_id).where(
                            StudyResponseRecord.period_id == record.id,
                            StudyResponseRecord.invalidated.is_(False),
                        )
                    )
                ).all()
            )
            if question_ids != set(QUESTION_RULES):
                raise ValueError("all required bounded responses are required")
            record.completed_at = record.completed_at or datetime.now(UTC)

    async def withdraw(self, participant_id: str) -> None:
        async with self._session_factory() as session, session.begin():
            participant = await session.get(
                StudyParticipantRecord, participant_id, with_for_update=True
            )
            if participant and participant.withdrawn_at is None:
                participant.withdrawn_at = datetime.now(UTC)
                session.add(
                    StudyConsentRecord(
                        id=f"consent-{uuid4().hex}",
                        participant_id=participant_id,
                        version=f"{CONSENT_VERSION}-withdrawal-{uuid4().hex[:8]}",
                        wording_hash=_hash("withdrawal"),
                        status="withdrawn",
                        acknowledgement_codes="withdrawal",
                        recorded_at=datetime.now(UTC),
                    )
                )

    async def delete_participant(self, participant_id: str) -> None:
        async with self._session_factory() as session, session.begin():
            participant = await session.get(
                StudyParticipantRecord, participant_id, with_for_update=True
            )
            if participant:
                await session.merge(
                    StudyDeletionTombstoneRecord(
                        code_hash=participant.opaque_code_hash,
                        deleted_at=datetime.now(UTC),
                    )
                )
            await session.execute(
                delete(StudyParticipantRecord).where(StudyParticipantRecord.id == participant_id)
            )

    async def _next_period(self, session: AsyncSession, participant_id: str) -> int:
        periods = (
            await session.scalars(
                select(StudyPeriodRecord)
                .where(StudyPeriodRecord.participant_id == participant_id)
                .order_by(StudyPeriodRecord.period)
            )
        ).all()
        return next((item.period for item in periods if item.completed_at is None), 2)

    async def _period(
        self,
        session: AsyncSession,
        participant_id: str,
        period: int,
        *,
        for_update: bool = False,
    ) -> StudyPeriodRecord:
        statement = select(StudyPeriodRecord).where(
            StudyPeriodRecord.participant_id == participant_id,
            StudyPeriodRecord.period == period,
        )
        if for_update:
            statement = statement.with_for_update()
        record = await session.scalar(statement)
        if not record:
            raise ValueError("assigned period is unavailable")
        return record

    @staticmethod
    def _validate_response(response: ResponseInput) -> None:
        rule = QUESTION_RULES.get(response.question_id)
        if not rule:
            raise ValueError("undeclared question")
        kind, options = rule
        if kind == "rating" and (response.rating is None or response.option_code is not None):
            raise ValueError("rating question requires one bounded rating")
        if kind == "option" and (
            response.option_code not in options or response.rating is not None
        ):
            raise ValueError("option question requires one declared option code")

    @staticmethod
    def _interval_watermark(interval: dict[str, object]) -> str:
        claims = cast(list[dict[str, object]], interval["claims"])
        return _hash(
            PROTOCOL_VERSION,
            str(interval["id"]),
            *(f"{item['source_id']}:{item['source_hash']}" for item in claims),
        )

    @staticmethod
    def _interval(interval_id: str) -> dict[str, object]:
        intervals = cast(list[dict[str, object]], _corpus()["intervals"])
        for interval in intervals:
            if interval["id"] == interval_id:
                return interval
        raise ValueError("frozen interval is unavailable")
