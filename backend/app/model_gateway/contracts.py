"""Provider-neutral model decision contracts."""

from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class DecisionAction(StrEnum):
    WAIT = "wait"
    MOVE = "move"


class AgentDecisionProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: DecisionAction
    affordance_id: str = Field(min_length=1, max_length=128)
    rationale_summary: str = Field(min_length=1, max_length=240)
    observation_ids: list[str] = Field(max_length=32)
    observation_watermark: str = Field(min_length=64, max_length=64)


class ModelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    task: str
    prompt: str
    output_schema: dict[str, object]
    timeout_seconds: float
    max_output_tokens: int
    correlation_id: str


class ModelOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    provider: str
    model: str
    provider_request_id: str | None = None
    finish_reason: str | None = None
    output: dict[str, object] | None = None
    failure_code: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int


class ModelGateway(Protocol):
    async def complete(self, request: ModelRequest) -> ModelOutcome: ...
