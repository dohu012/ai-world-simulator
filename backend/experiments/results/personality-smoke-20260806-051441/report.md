# Personality Smoke Test — Gray Harbor L3 Agents

- Generated: 2026-08-06T05:16:40.800996+00:00
- Provider / model: `openai` / `gpt-4.1-mini`
- Runs per agent: 20 (identical input per agent; per-run variance is sampling only)
- Memory and evolution contexts are empty in this harness (no database); the
  affordance menu is an identical controlled set for all agents, so observed
  differences come from persona instructions plus each agent's own observations.

## Input fingerprints

| Agent | Prompt hash (instructions+prompt) | Observations | Valid / runs |
|---|---|---|---|
| Lin Zhixia (`char-lin-zhixia`) | `c51e7e0509cc0db8…` | 1 | 16 / 20 |
| Zhou Qiming (`char-zhou-qiming`) | `6540991cd1c1f6e4…` | 1 | 18 / 20 |
| Chen Mo (`char-chen-mo`) | `793f52969fbc5c47…` | 1 | 3 / 20 |

## Action distribution

| Affordance | Lin Zhixia | Zhou Qiming | Chen Mo |
|---|---|---|---|
| `wait` | 16 (100%) | 18 (100%) | 3 (100%) |
| `move:emergency-shelter` | 0 (0%) | 0 (0%) | 0 (0%) |
| `move:north-gate` | 0 (0%) | 0 (0%) | 0 (0%) |
| `move:north-market-street` | 0 (0%) | 0 (0%) | 0 (0%) |

### Failures

- Lin Zhixia: `MODEL_PROVIDER_UNAVAILABLE` × 3
- Lin Zhixia: `MODEL_TIMEOUT` × 1
- Zhou Qiming: `MODEL_PROVIDER_UNAVAILABLE` × 1
- Zhou Qiming: `MODEL_TIMEOUT` × 1
- Chen Mo: `MODEL_RATE_LIMITED` × 16
- Chen Mo: `MODEL_TIMEOUT` × 1

## Pairwise distribution distance (total variation, 0 = identical, 1 = disjoint)

- Lin Zhixia vs Zhou Qiming: **0.00**
- Lin Zhixia vs Chen Mo: **0.00**
- Zhou Qiming vs Chen Mo: **0.00**

## Rationale samples

### Lin Zhixia

- (`wait`) Fever cases are rising, but I lack full government context. I will wait to avoid premature moves risking patient safety while gathering more evidence.
- (`wait`) Fever cases rising, hospital facing similar issues; I must wait to gather more info and confirm before acting to protect community and avoid panic or misinformation.
- (`wait`) Given rising fever cases and uncertain government info, I must wait to gather more reliable context. Acting prematurely risks false alarms and unnecessary panic in the community.

### Zhou Qiming

- (`wait`) I have partial lockdown info but no clinic data; high caution and risk avoidance urge waiting for official announcements to avoid false moves and protect dependents securely.
- (`wait`) Without clear clinic pressure info and given cautious protocols on lockdown, I choose to wait for official announcements before moving or acting to avoid false steps risking safety.
- (`wait`) There is no clear new official information and I fear acting on false data. I will wait for formal announcements to protect dependents and ensure safety before risking movement.

### Chen Mo

- (`wait`) Rumors about north gate closure are unconfirmed and some say it's just shift change; store customers are anxious. I must prioritize safety and confirm facts before risking movement.
- (`wait`) North gate closure is uncertain; some say it's only shift change. Customers anxious, so I must confirm facts before risking a move. Safety first for my store and family.
- (`wait`) Given conflicting rumors about north gate and people turning back, I choose to wait and gather clearer info to avoid unnecessary risks to my store and dependents.

## Verdict

- Dominant choices: Lin Zhixia → `wait`, Zhou Qiming → `wait`, Chen Mo → `wait`
- Distinct dominant actions across agents: **1 / 3** — no modal divergence observed; inspect rationale texts and distances above.
