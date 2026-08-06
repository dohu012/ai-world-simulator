# TASK-024 completion status

Status: **Incomplete, expansion deferred**

Repository work begun on 2026-07-31 and continued on 2026-08-03 added a staging architecture, Caddy policy,
pre-issued expiring HMAC-hashed access codes, database freeze triggers, a
server-side 24-hour return fence, Redis rate limits, private code revocation,
deletion tombstones, backup/reconciliation scripts, threat model, ADR and
runbooks.

Recorded technical evidence:

- migration `20260731_0014` upgraded the real PostgreSQL database and Alembic
  reported no drift;
- the final backend run passed 230 tests with 30 infrastructure skips; Ruff and
  strict mypy passed across 70 source files;
- the final infrastructure-enabled run passed 260 tests on a fresh PostgreSQL
  18.4 container after fixing a pre-existing non-isolated memory fixture;
- frontend unit tests passed 37/37 and TypeScript, ESLint, Prettier and the Next
  production build passed;
- Chrome Playwright plus axe passed 1/1 with no serious or critical violation;
- PostgreSQL 18.4 `pg_dump` produced `pilot-host18.dump` (338,112 bytes); isolated
  restore reached Alembic `20260731_0014` with all three pilot tables; a simulated
  deleted-participant resurrection was removed by tombstone reconciliation;
- 32 concurrent code issuance/activation/cleanup passed in 3.03 seconds, below
  the preregistered 10-second test budget;
- a fresh 0001-to-0014 migration, 0014 downgrade/re-upgrade and Alembic drift
  check passed after fixing the historical 0006 duplicate-column fresh-install
  defect.

The 2026-08-03 npm findings were remediated without a major framework upgrade:
Next 15.5.22 is locked with PostCSS 8.5.25 and Sharp 0.35.3, and the final full
npm audit reports zero vulnerabilities. Public enrollment remains stopped for
TLS/manual-accessibility, container supply-chain and human-evidence gates.

Docker Scout on official `postgres:18.4-alpine` digest `9a8afca54e78` reports
1 critical and 16 high findings, all from Go 1.24.6 embedded in
`/usr/local/bin/gosu`. The published tag is current but has not been rebuilt with
the fixed Go standard library. Removing gosu would break the official image's
initialization/privilege boundary, so enrollment remains stopped pending a fixed
upstream image and clean rescan. API/frontend image construction also could not
finish because Docker Hub token access timed out; this is recorded as a failed
supply-chain gate, not a successful build.

No public deployment was approved or operated. No recruitment window,
compensation, processor/region, TLS renewal, clean container scan, manual
screen-reader result, actual cost, incident
record or teardown evidence exists. Most importantly, zero real participants
completed both periods. This does not satisfy TASK-024's non-negotiable
completion rule and must not be represented as human evidence.

Evidence class is directional (`n=0`). Primary, order, carryover, missingness,
safety, return, accessibility and demand estimates are unavailable. TASK-025 is
therefore **defer expansion**. The next action is product-owner approval and
execution of the frozen recruitment/deployment window, not a Stage-2 feature.
