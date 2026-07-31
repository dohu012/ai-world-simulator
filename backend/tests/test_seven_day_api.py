from app.core.config import Settings
from app.main import create_app


def test_openapi_exposes_bounded_seven_day_commands() -> None:
    paths = create_app(Settings()).openapi()["paths"]
    assert {
        "/demo/worlds/gray-harbor/scenario",
        "/demo/worlds/gray-harbor/scenario/reset",
        "/demo/worlds/gray-harbor/me/scenario",
        "/demo/worlds/gray-harbor/me/scenario/affordances",
    } <= set(paths)


def test_owner_endpoint_requires_existing_caller_boundary() -> None:
    operation = create_app(Settings()).openapi()["paths"]["/demo/worlds/gray-harbor/me/scenario"][
        "get"
    ]
    assert any(
        parameter["name"] == "X-Demo-Agent-Id" and parameter["in"] == "header"
        for parameter in operation["parameters"]
    )
