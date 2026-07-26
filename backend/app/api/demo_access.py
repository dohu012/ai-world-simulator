"""Demo-only caller identity helpers."""

from typing import Annotated

from fastapi import Header

from app.api.errors import ApiError

DEMO_AGENT_ID_HEADER = "X-Demo-Agent-Id"
DEMO_SPECIAL_AGENT_IDS = frozenset({"char-lin-zhixia", "char-zhou-qiming", "char-chen-mo"})


async def require_demo_agent_id(
    demo_agent_id: Annotated[str | None, Header(alias=DEMO_AGENT_ID_HEADER)] = None,
) -> str:
    """Read the fixed demo caller identity from a header."""
    if demo_agent_id is None or demo_agent_id.strip() == "":
        raise ApiError(
            status_code=401,
            code="DEMO_AGENT_ID_REQUIRED",
            message="X-Demo-Agent-Id header is required for this demo endpoint.",
            details={"header": DEMO_AGENT_ID_HEADER},
        )
    if demo_agent_id not in DEMO_SPECIAL_AGENT_IDS:
        raise ApiError(
            status_code=403,
            code="DEMO_AGENT_FORBIDDEN",
            message="Demo agent is not allowed to use this endpoint.",
            details={"agent_id": demo_agent_id},
        )
    return demo_agent_id
