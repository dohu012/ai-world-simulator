from app.core.config import Settings
from app.main import create_app


def test_runtime_defaults_disabled_and_openapi_exposes_bounded_commands() -> None:
    assert Settings().world_runtime_enabled is False
    paths = create_app(Settings()).openapi()["paths"]
    expected = {
        "/demo/worlds/gray-harbor/runtime/start",
        "/demo/worlds/gray-harbor/runtime/pause",
        "/demo/worlds/gray-harbor/runtime/resume",
        "/demo/worlds/gray-harbor/runtime/advance",
        "/demo/worlds/gray-harbor/runtime",
        "/demo/worlds/gray-harbor/oracle-requests",
        "/demo/worlds/gray-harbor/oracle-requests/{request_id}/responses",
        "/demo/worlds/gray-harbor/notifications",
    }
    assert expected <= set(paths)
