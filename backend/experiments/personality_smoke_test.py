"""Personality smoke test: do different L3 personas produce observable behavior differences?

Standalone read-only experiment harness. It loads the fixed Gray Harbor demo world
in memory (no database), builds production-shaped decision prompts through the real
`build_decision_instructions` composer, and samples the configured ModelGateway N
times per agent under an identical, controlled affordance menu. Nothing in the
production code path is modified or mutated.

Usage (from backend/):
    .venv/Scripts/python experiments/personality_smoke_test.py --runs 20

The model provider comes from the regular settings (.env): set MODEL_PROVIDER=openai
plus MODEL_API_KEY for a real run, or MODEL_PROVIDER=fake for a deterministic
pipeline check (the scripted gateway always picks the first affordance).
"""

import argparse
import asyncio
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import ValidationError

from app.application.agent_decision import (
    INPUT_VERSION,
    AgentDecisionApplicationService,
    build_decision_instructions,
)
from app.application.memory_service import RetrievalRead
from app.core.config import get_settings
from app.model_gateway.contracts import AgentDecisionProposal, ModelRequest
from app.model_gateway.factory import build_model_gateway
from app.services.demo_world import get_gray_harbor_agent_perspective

AGENT_IDS = ["char-lin-zhixia", "char-zhou-qiming", "char-chen-mo"]

# The seeded edge graph gives Lin and Zhou no outgoing edges (wait would be the only
# legal action), so the experiment controls the action space instead: every agent is
# offered the same menu, making persona instructions + private observations the only
# varying inputs. This is an experimental control, not world-consistent movement.
MOVE_TARGETS = ["emergency-shelter", "north-gate", "north-market-street"]

EMPTY_MEMORY_WATERMARK = sha256(b"personality-smoke-empty-memory").hexdigest()
EMPTY_EVOLUTION_WATERMARK = sha256(b"personality-smoke-empty-evolution").hexdigest()
CONCURRENCY = 1
TRANSIENT = {"MODEL_TIMEOUT", "MODEL_RATE_LIMITED", "MODEL_PROVIDER_UNAVAILABLE"}
MAX_TRIES = 5
BACKOFF_SECONDS = [2, 5, 10, 20]


def empty_memory_context() -> RetrievalRead:
    return RetrievalRead(
        id="retrieval-personality-smoke-empty",
        policy_version="memory-policy-v1",
        mode="lexical",
        context_watermark=EMPTY_MEMORY_WATERMARK,
        character_budget=4000,
        characters_used=0,
        candidates=[],
    )


class AgentCase:
    """Frozen per-agent experiment input: identical across all runs of that agent."""

    def __init__(self, agent_id: str) -> None:
        perspective = get_gray_harbor_agent_perspective(agent_id)
        if perspective is None:
            raise SystemExit(f"unknown demo agent: {agent_id}")
        self.agent_id = agent_id
        self.name = perspective.character.name
        observations = sorted(
            perspective.observations, key=lambda item: (item.observed_at, item.id)
        )[-32:]
        self.observation_ids = [item.id for item in observations]
        memory_context = empty_memory_context()
        evolution_context: dict[str, object] = {}
        self.watermark = AgentDecisionApplicationService._input_watermark(
            self.observation_ids, EMPTY_MEMORY_WATERMARK, EMPTY_EVOLUTION_WATERMARK
        )
        self.affordances: list[dict[str, Any]] = [
            {"id": "wait", "action": "wait", "parameters": {}}
        ] + [
            {
                "id": f"move:{target}",
                "action": "move",
                "parameters": {
                    "target_location_id": target,
                    "expected_character_version": perspective.character.version,
                    "expected_world_version": perspective.world.version,
                },
            }
            for target in sorted(MOVE_TARGETS)
        ]
        safe_input = {
            "input_version": INPUT_VERSION,
            "world": perspective.world.model_dump(mode="json"),
            "character": perspective.character.model_dump(mode="json"),
            "profile": perspective.agentProfile.model_dump(mode="json"),
            "observations": [item.model_dump(mode="json") for item in observations],
            "observation_ids": self.observation_ids,
            "observation_watermark": self.watermark,
            "memory_context": memory_context.model_dump(mode="json"),
            "evolution_context": evolution_context,
            "affordances": self.affordances,
        }
        self.prompt = json.dumps(
            safe_input, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        self.instructions = build_decision_instructions(
            perspective.character,
            perspective.agentProfile,
            memory_context,
            evolution_context,
        )
        self.prompt_hash = sha256(f"{self.instructions}\n{self.prompt}".encode()).hexdigest()
        self.offered = {item["id"]: item for item in self.affordances}


async def run_once(gateway: Any, case: AgentCase, run: int, settings: Any) -> dict[str, Any]:
    requested_at = datetime.now(UTC)
    request = ModelRequest(
        task="personality_smoke_test",
        prompt=case.prompt,
        instructions=case.instructions,
        output_schema=AgentDecisionProposal.model_json_schema(),
        timeout_seconds=settings.model_timeout_seconds,
        max_output_tokens=settings.model_max_output_tokens,
        correlation_id=f"smoke-{case.agent_id}-{run}",
    )
    try:
        for attempt in range(MAX_TRIES):
            outcome = await gateway.complete(request)
            if outcome.failure_code not in TRANSIENT or attempt == MAX_TRIES - 1:
                break
            await asyncio.sleep(BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)])
    except Exception as exc:  # keep one bad call from killing the whole experiment
        return {
            "agent_id": case.agent_id,
            "agent_name": case.name,
            "run": run,
            "requested_at": requested_at.isoformat(),
            "prompt_hash": case.prompt_hash,
            "provider": "unknown",
            "model": "unknown",
            "latency_ms": 0,
            "failure_code": f"GATEWAY_EXCEPTION:{type(exc).__name__}",
            "action": None,
            "affordance_id": None,
            "rationale": None,
        }
    row: dict[str, Any] = {
        "agent_id": case.agent_id,
        "agent_name": case.name,
        "run": run,
        "requested_at": requested_at.isoformat(),
        "prompt_hash": case.prompt_hash,
        "provider": outcome.provider,
        "model": outcome.model,
        "latency_ms": outcome.latency_ms,
        "failure_code": outcome.failure_code,
        "action": None,
        "affordance_id": None,
        "rationale": None,
    }
    if outcome.failure_code is not None:
        return row
    try:
        proposal = AgentDecisionProposal.model_validate(outcome.output)
    except ValidationError:
        row["failure_code"] = "MODEL_OUTPUT_INVALID"
        return row
    if (
        proposal.affordance_id not in case.offered
        or proposal.action.value != case.offered[proposal.affordance_id]["action"]
        or proposal.observation_watermark != case.watermark
        or proposal.observation_ids != case.observation_ids
    ):
        row["failure_code"] = "DECISION_OUTPUT_NOT_ALLOWED"
        return row
    row["action"] = proposal.action.value
    row["affordance_id"] = proposal.affordance_id
    row["rationale"] = proposal.rationale_summary
    return row


def total_variation(a: Counter, b: Counter, total_a: int, total_b: int) -> float:
    keys = set(a) | set(b)
    if not total_a or not total_b:
        return 0.0
    return 0.5 * sum(abs(a[key] / total_a - b[key] / total_b) for key in keys)


def render_report(
    cases: list[AgentCase], rows: list[dict[str, Any]], settings: Any, runs: int
) -> str:
    by_agent = {case.agent_id: [r for r in rows if r["agent_id"] == case.agent_id] for case in cases}
    choices = {
        case.agent_id: Counter(
            r["affordance_id"] for r in by_agent[case.agent_id] if r["affordance_id"]
        )
        for case in cases
    }
    valid = {agent_id: sum(counter.values()) for agent_id, counter in choices.items()}
    failures = {
        case.agent_id: Counter(
            r["failure_code"] for r in by_agent[case.agent_id] if r["failure_code"]
        )
        for case in cases
    }
    provider = next((r["provider"] for r in rows), "unknown")
    model = next((r["model"] for r in rows), "unknown")
    lines = [
        "# Personality Smoke Test — Gray Harbor L3 Agents",
        "",
        f"- Generated: {datetime.now(UTC).isoformat()}",
        f"- Provider / model: `{provider}` / `{model}`",
        f"- Runs per agent: {runs} (identical input per agent; per-run variance is sampling only)",
        "- Memory and evolution contexts are empty in this harness (no database); the",
        "  affordance menu is an identical controlled set for all agents, so observed",
        "  differences come from persona instructions plus each agent's own observations.",
        "",
        "## Input fingerprints",
        "",
        "| Agent | Prompt hash (instructions+prompt) | Observations | Valid / runs |",
        "|---|---|---|---|",
    ]
    for case in cases:
        lines.append(
            f"| {case.name} (`{case.agent_id}`) | `{case.prompt_hash[:16]}…` "
            f"| {len(case.observation_ids)} | {valid[case.agent_id]} / {runs} |"
        )
    all_options = [item["id"] for item in cases[0].affordances]
    lines += ["", "## Action distribution", "", "| Affordance | " + " | ".join(c.name for c in cases) + " |"]
    lines.append("|---|" + "---|" * len(cases))
    for option in all_options:
        cells = []
        for case in cases:
            count = choices[case.agent_id][option]
            share = f" ({count / valid[case.agent_id]:.0%})" if valid[case.agent_id] else ""
            cells.append(f"{count}{share}")
        lines.append(f"| `{option}` | " + " | ".join(cells) + " |")
    if any(failures.values()):
        lines += ["", "### Failures", ""]
        for case in cases:
            for code, count in sorted(failures[case.agent_id].items()):
                lines.append(f"- {case.name}: `{code}` × {count}")
    lines += ["", "## Pairwise distribution distance (total variation, 0 = identical, 1 = disjoint)", ""]
    for i, left in enumerate(cases):
        for right in cases[i + 1 :]:
            distance = total_variation(
                choices[left.agent_id],
                choices[right.agent_id],
                valid[left.agent_id],
                valid[right.agent_id],
            )
            lines.append(f"- {left.name} vs {right.name}: **{distance:.2f}**")
    lines += ["", "## Rationale samples", ""]
    for case in cases:
        lines.append(f"### {case.name}")
        lines.append("")
        seen: list[str] = []
        for r in by_agent[case.agent_id]:
            if r["rationale"] and r["rationale"] not in seen:
                seen.append(r["rationale"])
                lines.append(f"- (`{r['affordance_id']}`) {r['rationale']}")
            if len(seen) == 3:
                break
        if not seen:
            lines.append("- No valid proposals recorded.")
        lines.append("")
    dominant = {
        case.agent_id: (choices[case.agent_id].most_common(1)[0][0] if choices[case.agent_id] else None)
        for case in cases
    }
    distinct = len({value for value in dominant.values() if value is not None})
    lines += [
        "## Verdict",
        "",
        f"- Dominant choices: "
        + ", ".join(f"{case.name} → `{dominant[case.agent_id]}`" for case in cases),
        f"- Distinct dominant actions across agents: **{distinct} / {len(cases)}**"
        + (" — personas diverge at the level of modal behavior."
           if distinct > 1
           else " — no modal divergence observed; inspect rationale texts and distances above."),
    ]
    return "\n".join(lines) + "\n"


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=20, help="decisions per agent")
    parser.add_argument("--out", type=Path, default=None, help="output directory")
    args = parser.parse_args()
    settings = get_settings()
    gateway = build_model_gateway(settings)
    if settings.model_provider not in {"fake", "openai"}:
        print(
            f"WARNING: MODEL_PROVIDER={settings.model_provider!r} resolves to the disabled "
            "gateway; every call will fail with MODEL_PROVIDER_DISABLED.",
            file=sys.stderr,
        )
    cases = [AgentCase(agent_id) for agent_id in AGENT_IDS]
    out_dir = args.out or (
        Path(__file__).resolve().parent
        / "results"
        / f"personality-smoke-{datetime.now(UTC):%Y%m%d-%H%M%S}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def bounded(case: AgentCase, run: int) -> dict[str, Any]:
        async with semaphore:
            return await run_once(gateway, case, run, settings)

    tasks = [bounded(case, run) for case in cases for run in range(1, args.runs + 1)]
    rows = list(await asyncio.gather(*tasks))
    rows.sort(key=lambda r: (r["agent_id"], r["run"]))

    results_path = out_dir / "results.jsonl"
    with results_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    report_path = out_dir / "report.md"
    report_path.write_text(render_report(cases, rows, settings, args.runs), encoding="utf-8")
    ok = sum(1 for r in rows if r["affordance_id"])
    print(f"{ok}/{len(rows)} valid decisions")
    failure_counts = Counter(r["failure_code"] for r in rows if r["failure_code"])
    for code, count in failure_counts.most_common():
        print(f"  failure {code}: {count}")
    print(f"results: {results_path}")
    print(f"report:  {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
