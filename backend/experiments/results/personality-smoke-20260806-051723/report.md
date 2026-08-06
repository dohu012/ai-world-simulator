# Personality Smoke Test — Gray Harbor L3 Agents

- Generated: 2026-08-06T05:25:15.844185+00:00
- Provider / model: `openai` / `gpt-4.1-mini`
- Runs per agent: 20 (identical input per agent; per-run variance is sampling only)
- Memory and evolution contexts are empty in this harness (no database); the
  affordance menu is an identical controlled set for all agents, so observed
  differences come from persona instructions plus each agent's own observations.

## Input fingerprints

| Agent | Prompt hash (instructions+prompt) | Observations | Valid / runs |
|---|---|---|---|
| Lin Zhixia (`char-lin-zhixia`) | `c51e7e0509cc0db8…` | 1 | 20 / 20 |
| Zhou Qiming (`char-zhou-qiming`) | `6540991cd1c1f6e4…` | 1 | 20 / 20 |
| Chen Mo (`char-chen-mo`) | `793f52969fbc5c47…` | 1 | 20 / 20 |

## Action distribution

| Affordance | Lin Zhixia | Zhou Qiming | Chen Mo |
|---|---|---|---|
| `wait` | 20 (100%) | 20 (100%) | 20 (100%) |
| `move:emergency-shelter` | 0 (0%) | 0 (0%) | 0 (0%) |
| `move:north-gate` | 0 (0%) | 0 (0%) | 0 (0%) |
| `move:north-market-street` | 0 (0%) | 0 (0%) | 0 (0%) |

## Pairwise distribution distance (total variation, 0 = identical, 1 = disjoint)

- Lin Zhixia vs Zhou Qiming: **0.00**
- Lin Zhixia vs Chen Mo: **0.00**
- Zhou Qiming vs Chen Mo: **0.00**

## Rationale samples

### Lin Zhixia

- (`wait`) I must be cautious given rising fever cases and unclear government context. Waiting allows me to observe more and confirm the risk before moving or acting to protect my community safely.
- (`wait`) I choose to wait to avoid premature actions based on partial information. Rising medicine use and more fevers are concerning; I need to monitor carefully before advising or moving to protect patients and myself.
- (`wait`) I see rising fever cases and hear of similar cases at the hospital. Without full context on lockdowns, I will wait to avoid missteps and protect patients with caution.

### Zhou Qiming

- (`wait`) I choose to wait for official orders before acting, ensuring safety and avoiding risks from incomplete info. Lockdown plans are not fully public; cautious action keeps dependents safe.
- (`wait`) I lack full info on clinic pressure and must avoid false moves. Plan says wait for public messaging on north gate control, so I wait to protect safety and confirm before risk.
- (`wait`) I have partial info on lockdown plans but no data on clinic pressures. I must avoid acting on incomplete info and wait for formal announcements to ensure safety and accuracy.

### Chen Mo

- (`wait`) Rumors about north gate closing seem unconfirmed; cautious to avoid risk, better to wait and gather more reliable info before moving or risking my dependents' safety.
- (`wait`) Rumors of the north gate closing are unconfirmed and contradictory. I must avoid risk to protect my dependents and wait for clearer, reliable information before acting.
- (`wait`) Rumors say north gate may be closed but uncertain if shift change or lockdown. Customers anxious. I prefer to confirm before risking moving, to protect my store and dependents safely.

## Verdict

- Dominant choices: Lin Zhixia → `wait`, Zhou Qiming → `wait`, Chen Mo → `wait`
- Distinct dominant actions across agents: **1 / 3** — no modal divergence observed; inspect rationale texts and distances above.
