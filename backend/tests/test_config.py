from app.core.config import Settings


def test_settings_can_be_overridden(monkeypatch: object) -> None:
    monkeypatch.setenv("APP_PORT", "9000")  # type: ignore[attr-defined]
    settings = Settings()
    assert settings.app_port == 9000
