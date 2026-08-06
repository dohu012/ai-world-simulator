# Personality Smoke Test — Gray Harbor L3 Agents

- Generated: 2026-08-06T03:51:32.186178+00:00
- Provider / model: `openai` / `gpt-mini-4.1`
- Runs per agent: 20 (identical input per agent; per-run variance is sampling only)
- Memory and evolution contexts are empty in this harness (no database); the
  affordance menu is an identical controlled set for all agents, so observed
  differences come from persona instructions plus each agent's own observations.

## Input fingerprints

| Agent | Prompt hash (instructions+prompt) | Observations | Valid / runs |
|---|---|---|---|
| Lin Zhixia (`char-lin-zhixia`) | `c51e7e0509cc0db8…` | 1 | 0 / 20 |
| Zhou Qiming (`char-zhou-qiming`) | `6540991cd1c1f6e4…` | 1 | 0 / 20 |
| Chen Mo (`char-chen-mo`) | `793f52969fbc5c47…` | 1 | 0 / 20 |

## Action distribution

| Affordance | Lin Zhixia | Zhou Qiming | Chen Mo |
|---|---|---|---|
| `wait` | 0 | 0 | 0 |
| `move:emergency-shelter` | 0 | 0 | 0 |
| `move:north-gate` | 0 | 0 | 0 |
| `move:north-market-street` | 0 | 0 | 0 |

### Failures

- Lin Zhixia: `MODEL_PROVIDER_UNAVAILABLE` × 20
- Zhou Qiming: `MODEL_PROVIDER_UNAVAILABLE` × 20
- Chen Mo: `MODEL_PROVIDER_UNAVAILABLE` × 20

## Pairwise distribution distance (total variation, 0 = identical, 1 = disjoint)

- Lin Zhixia vs Zhou Qiming: **0.00**
- Lin Zhixia vs Chen Mo: **0.00**
- Zhou Qiming vs Chen Mo: **0.00**

## Rationale samples

### Lin Zhixia

- No valid proposals recorded.

### Zhou Qiming

- No valid proposals recorded.

### Chen Mo

- No valid proposals recorded.

## Verdict

- Dominant choices: Lin Zhixia → `None`, Zhou Qiming → `None`, Chen Mo → `None`
- Distinct dominant actions across agents: **0 / 3** — no modal divergence observed; inspect rationale texts and distances above.
