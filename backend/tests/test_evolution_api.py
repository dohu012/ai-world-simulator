from app.core.config import Settings
from app.main import create_app


def test_openapi_exposes_owner_scoped_evolution_vertical_slice() -> None:
    operation = create_app(Settings()).openapi()["paths"]["/demo/worlds/gray-harbor/me/evolution"][
        "get"
    ]
    assert any(
        parameter["name"] == "X-Demo-Agent-Id" and parameter["in"] == "header"
        for parameter in operation["parameters"]
    )
    assert "/demo/worlds/gray-harbor/me/reflections" in create_app(Settings()).openapi()["paths"]
