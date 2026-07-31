from collections.abc import AsyncIterator
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.routes import product_validation
from app.application.product_validation_service import EnrollmentResult


class FakeService:
    async def enroll(self, **_: object) -> EnrollmentResult:
        return EnrollmentResult(
            participant_id="study-test",
            sequence="AB",
            assignment_version="sha256-balanced-block-v1",
            next_period=1,
        )

    async def authenticate(
        self, access_code: str, *, include_withdrawn: bool = False
    ) -> SimpleNamespace:
        del include_withdrawn
        if access_code != "abcdefghijklmnop":
            raise ValueError
        return SimpleNamespace(id="study-test")


@pytest.fixture
async def playtest_client(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[AsyncClient]:
    monkeypatch.setattr(product_validation, "service", lambda _request: FakeService())
    app = FastAPI()
    app.state.settings = SimpleNamespace(study_enrollment_enabled=True, study_admin_key=None)
    app.include_router(product_validation.router)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


async def test_protocol_is_public_frozen_and_no_store(playtest_client: AsyncClient) -> None:
    response = await playtest_client.get("/playtest/protocol")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["free_text_collected"] is False
    assert len(response.json()["content_hash"]) == 64


async def test_enrollment_requires_csrf_and_bounded_acknowledgements(
    playtest_client: AsyncClient,
) -> None:
    body = {
        "access_code": "abcdefghijklmnop",
        "acknowledgement_codes": ["fiction", "bounded_data", "withdrawal"],
        "device_class": "desktop",
    }
    denied = await playtest_client.post("/playtest/enroll", json=body)
    assert denied.status_code == 403
    accepted = await playtest_client.post(
        "/playtest/enroll", json=body, headers={"X-CSRF-Token": "playtest-v1"}
    )
    assert accepted.status_code == 200
    assert accepted.json()["sequence"] == "AB"
    assert accepted.headers["content-security-policy"].startswith("default-src 'self'")


async def test_access_errors_are_indistinguishable(playtest_client: AsyncClient) -> None:
    response = await playtest_client.get(
        "/playtest/me", headers={"X-Study-Access-Code": "wrong-code-value!"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "study access is unavailable"
