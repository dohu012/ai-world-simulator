"""Tests for the public domain data contracts."""

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from app.domain.actions import ActionIntent, ActionResult
from app.domain.character import AgentProfile, Character
from app.domain.export_schemas import export_schemas
from app.domain.facts import AgentBelief, WorldFact
from app.domain.oracle import OracleRequest, OracleResponse
from app.domain.schemas import DOMAIN_MODELS
from app.domain.world import World

FIXTURES = Path(__file__).parent / "fixtures" / "domain"
MODEL_FIXTURES: dict[type[BaseModel], str] = {
    model: f"{slug.replace('-', '_')}.json" for slug, model in DOMAIN_MODELS.items()
}


def fixture_text(model: type[BaseModel]) -> str:
    """Load the canonical JSON example for a model."""
    return (FIXTURES / MODEL_FIXTURES[model]).read_text(encoding="utf-8")


def fixture_data(model: type[BaseModel]) -> dict[str, Any]:
    """Load an example as mutable test data."""
    value = json.loads(fixture_text(model))
    assert isinstance(value, dict)
    return value


@pytest.mark.parametrize("model", DOMAIN_MODELS.values(), ids=DOMAIN_MODELS.keys())
def test_every_fixture_is_valid(model: type[BaseModel]) -> None:
    instance = model.model_validate_json(fixture_text(model))
    assert instance.schema_version == "1.0"


@pytest.mark.parametrize("model", DOMAIN_MODELS.values(), ids=DOMAIN_MODELS.keys())
def test_json_round_trip_preserves_fields(model: type[BaseModel]) -> None:
    first = model.model_validate_json(fixture_text(model))
    second = model.model_validate_json(first.model_dump_json())
    assert second.model_dump(mode="json") == first.model_dump(mode="json")


@pytest.mark.parametrize("model", DOMAIN_MODELS.values(), ids=DOMAIN_MODELS.keys())
def test_unknown_fields_are_rejected(model: type[BaseModel]) -> None:
    data = fixture_data(model)
    data["unknown_field"] = "should fail"
    with pytest.raises(ValidationError):
        model.model_validate_json(json.dumps(data))


def test_naive_datetime_is_rejected() -> None:
    data = fixture_data(World)
    data["current_time"] = "2026-07-23T12:00:00"
    with pytest.raises(ValidationError):
        World.model_validate_json(json.dumps(data))


@pytest.mark.parametrize(
    ("model", "field", "value"),
    [
        (Character, "health", 1.1),
        (AgentBelief, "confidence", -0.1),
        (OracleResponse, "clarity", 1.1),
        (World, "time_scale", 0.0),
    ],
)
def test_numeric_ranges(model: type[BaseModel], field: str, value: float) -> None:
    data = fixture_data(model)
    data[field] = value
    with pytest.raises(ValidationError):
        model.model_validate_json(json.dumps(data))


def test_profile_weight_range() -> None:
    data = fixture_data(AgentProfile)
    data["traits"]["cautious"] = 1.1
    with pytest.raises(ValidationError):
        AgentProfile.model_validate_json(json.dumps(data))


def test_world_fact_rejects_reversed_validity() -> None:
    data = fixture_data(WorldFact)
    data["valid_until"] = "2026-07-23T11:54:00+08:00"
    with pytest.raises(ValidationError):
        WorldFact.model_validate_json(json.dumps(data))


def test_succeeded_action_rejects_failure_reason() -> None:
    data = fixture_data(ActionResult)
    data["status"] = "succeeded"
    with pytest.raises(ValidationError):
        ActionResult.model_validate_json(json.dumps(data))


def test_oracle_request_rejects_past_real_deadline() -> None:
    data = fixture_data(OracleRequest)
    data["real_deadline"] = "2026-07-23T12:02:00+08:00"
    with pytest.raises(ValidationError):
        OracleRequest.model_validate_json(json.dumps(data))


@pytest.mark.parametrize(
    ("model", "forbidden_field"),
    [
        (ActionIntent, "success"),
        (ActionIntent, "state_changes"),
        (WorldFact, "confidence"),
        (AgentBelief, "visibility"),
        (OracleResponse, "selected_action"),
    ],
)
def test_domain_boundary_fields_are_absent_and_rejected(
    model: type[BaseModel], forbidden_field: str
) -> None:
    assert forbidden_field not in model.model_fields
    data = fixture_data(model)
    data[forbidden_field] = "not allowed"
    with pytest.raises(ValidationError):
        model.model_validate_json(json.dumps(data))


def test_schema_export_is_complete_valid_and_deterministic(tmp_path: Path) -> None:
    first = export_schemas(tmp_path)
    second = export_schemas(tmp_path)
    assert first == second
    assert set(first) == {f"{slug}.schema.json" for slug in DOMAIN_MODELS}

    for slug, model in DOMAIN_MODELS.items():
        schema = json.loads((tmp_path / f"{slug}.schema.json").read_text(encoding="utf-8"))
        assert schema["type"] == "object"
        assert set(model.model_fields).issubset(schema["properties"])
        assert "schema_version" in schema["required"]
