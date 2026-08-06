"""Privacy-minimized public boundary for the frozen TASK-023 study."""

import hmac
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, Response
from pydantic import BaseModel, Field

from app.application.product_validation_service import (
    AggregateState,
    EnrollmentResult,
    ParticipantState,
    ProbeInput,
    ProductValidationService,
    ResponseInput,
    frozen_protocol,
)
from app.domain.product_validation import Presentation

router = APIRouter(prefix="/playtest", tags=["controlled-playtest"])


class EnrollmentInput(BaseModel):
    access_code: str = Field(min_length=16, max_length=128)
    acknowledgement_codes: set[str] = Field(min_length=3, max_length=3)
    device_class: str = Field(default="unknown", max_length=24)


class ResponseResult(BaseModel):
    response_id: str


class AccessCodeIssueInput(BaseModel):
    ttl_hours: int = Field(default=168, ge=1, le=720)


class AccessCodeIssueResult(BaseModel):
    access_code: str
    expires_at: datetime


class AccessCodeRevokeInput(BaseModel):
    access_code: str = Field(min_length=16, max_length=128)


def service(request: Request) -> ProductValidationService:
    settings = request.app.state.settings
    return ProductValidationService(
        request.app.state.database.session_factory,
        code_pepper=settings.study_code_pepper,
        min_return_hours=settings.study_min_return_hours,
    )


async def enforce_rate_limit(request: Request, bucket: str) -> None:
    redis = getattr(request.app.state, "redis", None)
    if redis is None:
        return
    settings = request.app.state.settings
    key = f"study-rate:{bucket}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, getattr(settings, "study_rate_limit_window_seconds", 60))
    if count > getattr(settings, "study_rate_limit_attempts", 12):
        raise HTTPException(status_code=429, detail="request could not be accepted")


def no_store(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"


def require_csrf(
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    if x_csrf_token != "playtest-v1":
        raise HTTPException(status_code=403, detail="request could not be accepted")


async def participant_id(
    request: Request, access_code: str | None, *, include_withdrawn: bool = False
) -> str:
    await enforce_rate_limit(
        request,
        hmac.new(
            (getattr(request.app.state.settings, "study_code_pepper", None) or "disabled").encode(),
            (access_code or "").encode(),
            "sha256",
        ).hexdigest(),
    )
    try:
        participant = await service(request).authenticate(
            access_code or "", include_withdrawn=include_withdrawn
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail="study access is unavailable") from error
    return participant.id


@router.get("/protocol")
async def protocol(response: Response) -> dict[str, object]:
    no_store(response)
    return frozen_protocol()


@router.post("/enroll", response_model=EnrollmentResult)
async def enroll(
    request: Request,
    response: Response,
    body: EnrollmentInput,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> EnrollmentResult:
    no_store(response)
    require_csrf(x_csrf_token)
    await enforce_rate_limit(
        request,
        hmac.new(
            (getattr(request.app.state.settings, "study_code_pepper", None) or "disabled").encode(),
            body.access_code.encode(),
            "sha256",
        ).hexdigest(),
    )
    if not request.app.state.settings.study_enrollment_enabled:
        raise HTTPException(status_code=503, detail="study enrollment is paused")
    try:
        return await service(request).enroll(**body.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/me", response_model=ParticipantState)
async def state(
    request: Request,
    response: Response,
    x_study_access_code: Annotated[str | None, Header(alias="X-Study-Access-Code")] = None,
) -> ParticipantState:
    no_store(response)
    identity = await participant_id(request, x_study_access_code)
    return await service(request).state(identity)


@router.get("/me/periods/{period}/presentation", response_model=Presentation)
async def presentation(
    request: Request,
    response: Response,
    period: int,
    x_study_access_code: Annotated[str | None, Header(alias="X-Study-Access-Code")] = None,
) -> Presentation:
    no_store(response)
    identity = await participant_id(request, x_study_access_code)
    try:
        return await service(request).presentation(identity, period)
    except ValueError as error:
        raise HTTPException(status_code=404, detail="assigned period is unavailable") from error


@router.post("/me/periods/{period}/exposure", status_code=204)
async def complete_exposure(
    request: Request,
    response: Response,
    period: int,
    x_study_access_code: Annotated[str | None, Header(alias="X-Study-Access-Code")] = None,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    no_store(response)
    require_csrf(x_csrf_token)
    identity = await participant_id(request, x_study_access_code)
    await service(request).complete_exposure(identity, period)


@router.post("/me/periods/{period}/return", status_code=204)
async def mark_return(
    request: Request,
    response: Response,
    period: int,
    x_study_access_code: Annotated[str | None, Header(alias="X-Study-Access-Code")] = None,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    no_store(response)
    require_csrf(x_csrf_token)
    identity = await participant_id(request, x_study_access_code)
    try:
        await service(request).mark_return(identity, period)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/me/periods/{period}/responses", response_model=ResponseResult)
async def respond(
    request: Request,
    response: Response,
    period: int,
    body: ResponseInput,
    x_study_access_code: Annotated[str | None, Header(alias="X-Study-Access-Code")] = None,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> ResponseResult:
    no_store(response)
    require_csrf(x_csrf_token)
    identity = await participant_id(request, x_study_access_code)
    try:
        response_id = await service(request).respond(identity, period, body, idempotency_key or "")
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return ResponseResult(response_id=response_id)


@router.post("/me/responses/{response_id}/corrections", response_model=ResponseResult)
async def correct(
    request: Request,
    response: Response,
    response_id: str,
    body: ResponseInput,
    x_study_access_code: Annotated[str | None, Header(alias="X-Study-Access-Code")] = None,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> ResponseResult:
    no_store(response)
    require_csrf(x_csrf_token)
    identity = await participant_id(request, x_study_access_code)
    try:
        corrected_id = await service(request).correct(
            identity, response_id, body, idempotency_key or ""
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return ResponseResult(response_id=corrected_id)


@router.post("/me/demand-probes", status_code=204)
async def probe(
    request: Request,
    response: Response,
    body: ProbeInput,
    x_study_access_code: Annotated[str | None, Header(alias="X-Study-Access-Code")] = None,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    no_store(response)
    require_csrf(x_csrf_token)
    identity = await participant_id(request, x_study_access_code)
    try:
        await service(request).submit_probe(identity, body)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/me/periods/{period}/complete", status_code=204)
async def complete_period(
    request: Request,
    response: Response,
    period: int,
    x_study_access_code: Annotated[str | None, Header(alias="X-Study-Access-Code")] = None,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    no_store(response)
    require_csrf(x_csrf_token)
    identity = await participant_id(request, x_study_access_code)
    try:
        await service(request).complete_period(identity, period)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.post("/me/withdraw", status_code=204)
async def withdraw(
    request: Request,
    response: Response,
    x_study_access_code: Annotated[str | None, Header(alias="X-Study-Access-Code")] = None,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    no_store(response)
    require_csrf(x_csrf_token)
    identity = await participant_id(request, x_study_access_code)
    await service(request).withdraw(identity)


@router.delete("/me", status_code=204)
async def delete_me(
    request: Request,
    response: Response,
    x_study_access_code: Annotated[str | None, Header(alias="X-Study-Access-Code")] = None,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    no_store(response)
    require_csrf(x_csrf_token)
    identity = await participant_id(request, x_study_access_code, include_withdrawn=True)
    await service(request).delete_participant(identity)


@router.get("/admin/report", response_model=AggregateState)
async def aggregate_report(
    request: Request,
    response: Response,
    x_study_admin_key: Annotated[str | None, Header(alias="X-Study-Admin-Key")] = None,
) -> AggregateState:
    no_store(response)
    configured = request.app.state.settings.study_admin_key
    if not configured or not hmac.compare_digest(x_study_admin_key or "", configured):
        raise HTTPException(status_code=404, detail="study access is unavailable")
    return await service(request).aggregate_state()


@router.post("/admin/access-codes", response_model=AccessCodeIssueResult)
async def issue_access_code(
    request: Request,
    response: Response,
    body: AccessCodeIssueInput,
    x_study_admin_key: Annotated[str | None, Header(alias="X-Study-Admin-Key")] = None,
) -> AccessCodeIssueResult:
    no_store(response)
    configured = request.app.state.settings.study_admin_key
    if not configured or not hmac.compare_digest(x_study_admin_key or "", configured):
        raise HTTPException(status_code=404, detail="study access is unavailable")
    try:
        access_code, expires_at = await service(request).issue_access_code(ttl_hours=body.ttl_hours)
    except ValueError as error:
        raise HTTPException(status_code=503, detail="study access is unavailable") from error
    return AccessCodeIssueResult(access_code=access_code, expires_at=expires_at)


@router.post("/admin/access-codes/revoke", status_code=204)
async def revoke_access_code(
    request: Request,
    response: Response,
    body: AccessCodeRevokeInput,
    x_study_admin_key: Annotated[str | None, Header(alias="X-Study-Admin-Key")] = None,
) -> None:
    no_store(response)
    configured = request.app.state.settings.study_admin_key
    if not configured or not hmac.compare_digest(x_study_admin_key or "", configured):
        raise HTTPException(status_code=404, detail="study access is unavailable")
    await service(request).revoke_access_code(body.access_code)
