import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_can_be_overridden(monkeypatch: object) -> None:
    monkeypatch.setenv("APP_PORT", "9000")  # type: ignore[attr-defined]
    settings = Settings()
    assert settings.app_port == 9000


def test_production_enrollment_requires_https_and_strong_study_secrets() -> None:
    with pytest.raises(ValidationError, match="32-byte admin key"):
        Settings(app_env="production", study_enrollment_enabled=True)
    with pytest.raises(ValidationError, match="HTTPS origins"):
        Settings(
            app_env="production",
            study_enrollment_enabled=True,
            study_admin_key="a" * 32,
            study_code_pepper="b" * 32,
            cors_origins=["http://pilot.example"],
        )
    accepted = Settings(
        app_env="production",
        study_enrollment_enabled=True,
        study_admin_key="a" * 32,
        study_code_pepper="b" * 32,
        cors_origins=["https://pilot.example"],
        trusted_hosts=["pilot.example"],
    )
    assert accepted.trusted_hosts == ["pilot.example"]
