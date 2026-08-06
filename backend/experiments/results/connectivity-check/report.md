# Personality Smoke Test — Gray Harbor L3 Agents

- Generated: 2026-08-06T05:14:21.281661+00:00
- Provider / model: `openai` / `gpt-4.1-mini`
- Runs per agent: 2 (identical input per agent; per-run variance is sampling only)
- Memory and evolution contexts are empty in this harness (no database); the
  affordance menu is an identical controlled set for all agents, so observed
  differences come from persona instructions plus each agent's own observations.

## Input fingerprints

| Agent | Prompt hash (instructions+prompt) | Observations | Valid / runs |
|---|---|---|---|
| Lin Zhixia (`char-lin-zhixia`) | `c51e7e0509cc0db8…` | 1 | 2 / 2 |
| Zhou Qiming (`char-zhou-qiming`) | `6540991cd1c1f6e4…` | 1 | 2 / 2 |
| Chen Mo (`char-chen-mo`) | `793f52969fbc5c47…` | 1 | 2 / 2 |

## Action distribution

| Affordance | Lin Zhixia | Zhou Qiming | Chen Mo |
|---|---|---|---|
| `wait` | 2 (100%) | 2 (100%) | 2 (100%) |
| `move:emergency-shelter` | 0 (0%) | 0 (0%) | 0 (0%) |
| `move:north-gate` | 0 (0%) | 0 (0%) | 0 (0%) |
| `move:north-market-street` | 0 (0%) | 0 (0%) | 0 (0%) |

## Pairwise distribution distance (total variation, 0 = identical, 1 = disjoint)

- Lin Zhixia vs Zhou Qiming: **0.00**
- Lin Zhixia vs Chen Mo: **0.00**
- Zhou Qiming vs Chen Mo: **0.00**

## Rationale samples

### Lin Zhixia

- (`wait`) With rising medicine use and crowded clinic, I must avoid moving until I confirm government guidance to protect patients and myself from potentially worsening infection risks.
- (`wait`) Cases are rising and hospital overwhelmed; without full government info, I must carefully monitor and warn neighbors without moving to avoid spreading risk prematurely.

### Zhou Qiming

- (`wait`) I only have partial info on the lockdown plan and no clinic data; prudent to wait for formal public announcements before acting to avoid false alarms or unnecessary risk.
- (`wait`) I will wait for a formal announcement to avoid acting on incomplete information. Confirming details first protects my dependents and ensures I respond correctly to lockdown protocols.

### Chen Mo

- (`wait`) I hear conflicting rumors about the north gate and see anxious customers. To avoid risk and protect my dependents, I'll wait for clearer info before deciding to move.
- (`wait`) I sense anxiety and uncertain rumors about the north gate closure. To protect my dependents and avoid acting on false info, I will wait and gather clearer confirmation before moving or exposing risk.

## Verdict

- Dominant choices: Lin Zhixia → `wait`, Zhou Qiming → `wait`, Chen Mo → `wait`
- Distinct dominant actions across agents: **1 / 3** — no modal divergence observed; inspect rationale texts and distances above.
