from app.application.return_loop_service import ReturnLoopService
from app.core.config import Settings
from app.main import create_app


def test_fixed_projection_is_stable_and_source_linked() -> None:
    first = ReturnLoopService.fixed_summary("char-chen-mo")
    second = ReturnLoopService.fixed_summary("char-chen-mo")
    assert first.source_watermark == second.source_watermark
    assert len(first.claims) == 4
    assert all(claim.owner_id == "char-chen-mo" for claim in first.claims)
    assert all(claim.source_hash for claim in first.claims)


def test_openapi_requires_owner_csrf_and_idempotency_boundaries() -> None:
    paths = create_app(Settings()).openapi()["paths"]
    read = paths["/demo/worlds/gray-harbor/me/return-loop"]["get"]
    assert any(item["name"] == "X-Demo-Agent-Id" for item in read["parameters"])
    mutation = paths["/demo/worlds/gray-harbor/me/return-loop/inbox/{item_id}/{action}"]["post"]
    assert any(item["name"] == "X-CSRF-Token" for item in mutation["parameters"])
    event = paths["/demo/worlds/gray-harbor/me/return-loop/events/{event_code}"]["post"]
    assert any(item["name"] == "Idempotency-Key" for item in event["parameters"])
