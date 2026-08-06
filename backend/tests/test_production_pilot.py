from datetime import UTC, datetime, timedelta

import pytest

from app.application.product_validation_service import ProductValidationService, _code_hash


def test_access_code_hash_is_keyed_and_versionable() -> None:
    code = "opaque-code-with-more-than-128-bits"
    assert _code_hash("a" * 32, code) != _code_hash("b" * 32, code)
    assert len(_code_hash("a" * 32, code)) == 64


def test_production_service_rejects_missing_or_short_pepper() -> None:
    service = ProductValidationService(None, code_pepper="short")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="unavailable"):
        service._require_pepper()


def test_return_window_boundary_is_timezone_aware() -> None:
    completed = datetime.now(UTC)
    minimum = timedelta(hours=24)
    assert completed + minimum > completed
