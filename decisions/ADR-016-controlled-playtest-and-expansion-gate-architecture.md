# ADR-016: repository-native controlled playtest

Date: 2026-07-30  
Status: Accepted

Select repository-owned deterministic assignment, allowlisted coded events and
questionnaires, Python standard-library statistics, normalized PostgreSQL
persistence, a focused Next.js route, and Playwright/axe-compatible accessibility
tests. No analytics, experiment, survey, replay, or hosted deployment SDK is
added.

The measured local spike assigns 3,200 opaque identifiers reproducibly with less
than 5% imbalance, reproduces the golden aggregate without SciPy/R, suppresses
cells below five, rejects ambiguous TASK-022 wording, and returns `defer` below
eight participants.

| Candidate | Version reviewed | License | Decision / removal seam |
| --- | --- | --- | --- |
| repository native | repository 2026-07-30 | project | accept; delete isolated module/tables |
| GrowthBook | 4.x docs, accessed 2026-07-30 | MIT/core | reject now; server and SDK add no value at n=16 |
| Unleash | 7.x docs, accessed 2026-07-30 | Apache-2.0/core | reject now; operational surface exceeds need |
| Flagsmith | 2.x server docs, accessed 2026-07-30 | BSD-3-Clause/core | defer; removable SDK but unnecessary |
| PostHog | 2026 docs, accessed 2026-07-30 | MIT client/mixed server | reject; capture defaults and large surface |
| Matomo | 5.x docs, accessed 2026-07-30 | GPL-3.0 | defer; analytics not needed |
| Plausible CE | 3.x docs, accessed 2026-07-30 | AGPL-3.0 | defer; aggregate web analytics cannot score crossover |
| LimeSurvey CE | 6.x docs, accessed 2026-07-30 | GPL-2.0+ | defer; separate data store/deletion |
| Formbricks | 3.x docs, accessed 2026-07-30 | AGPL-3.0 | defer; more supply chain and capture surface |
| KoboToolbox | 2026 docs, accessed 2026-07-30 | AGPL-3.0 | defer; offline fieldwork strengths not required |
| SurveyJS | 2.x docs, accessed 2026-07-30 | MIT core | defer; native bounded form is smaller |
| Python stdlib | Python 3.12+ | PSF | accept; exact sign/Wilson/golden fixture |
| SciPy/statsmodels | current docs, accessed 2026-07-30 | BSD-3-Clause | defer; no measured advantage for frozen formulas |
| OpenTelemetry | 1.x spec | Apache-2.0 | defer; bounded counters suffice |
| axe-core | 4.x | MPL-2.0 | accept when installed; automation supplements manual review |
| Playwright | 1.62.0 | Apache-2.0 | accept existing Chrome-channel setup |

Hosted Statsig, tunnels and survey SaaS are rejected for this internal protocol:
regions, subprocessors, raw network metadata, retention/deletion and price create
unnecessary uncertainty. Local facilitated testing is selected; any public
deployment requires a new operational approval.

Assignment never uses behavior or narrative state. Variants are read-only
projections over identical source sets. Protocols and question wording become
immutable after first enrollment. Human evidence cannot override privacy,
authority, provenance or copy failures.
