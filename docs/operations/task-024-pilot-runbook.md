# TASK-024 pilot runbook

## Before enrollment

1. Record owner, host/region, processors, start/end, cost and incident contact.
2. Generate `.env.pilot` outside Git with 32+ byte admin key/pepper; keep
   `STUDY_ENROLLMENT_ENABLED=false`.
3. Resolve every image to a digest, generate SBOM/vulnerability reports, and
   record repository/protocol/corpus/frontend hashes.
   Any high/critical production finding blocks enrollment unless a documented
   non-applicability review and owner approval exist.
4. Deploy staging, migrate through `20260731_0014`, verify TLS redirect/renewal,
   public admin 404, CSP/no-store, generic invalid-code errors and log scans.
5. Run `scripts/pilot-backup.ps1`, restore with `pg_restore` to an isolated
   database, import the latest tombstones, run
   `scripts/pilot-reconcile-deletions.sql`, and prove deleted rows are absent.
   The `pg_dump` client major version must be at least the server major version;
   the measured development server is PostgreSQL 18.4.
6. Run full backend/frontend/browser/accessibility/load gates. Record failures,
   manual Narrator/keyboard/200%-zoom/forced-colors results and unsupported
   hardware. Obtain product-owner approval before enabling enrollment.

Issue one code through the private admin endpoint. Transmit it separately; never
put it in a URL, ticket, screenshot or analysis export. Keep issuance data
separate from answers.

## Daily operation

Check readiness, disk/database connections, latency/error counts, assignment
balance, missing sessions, backup age and deletion SLA without inspecting
outcome differences. Run one encrypted backup. A single neutral reminder is
allowed only where separately consented; the current repository has no reminder
sender, so operational reminders remain disabled.

## Incident and stop

Set `STUDY_ENROLLMENT_ENABLED=false`, restart API, preserve bounded evidence,
revoke affected codes/secrets and notify the owner. Stop for any source/privacy/
assignment/correction/deletion/accessibility/build-hash failure. Supersede the
protocol before restarting; never silently patch an enrolled cohort.

## Deletion and teardown

Authenticated deletion writes a keyed-hash tombstone and cascades row data.
Confirm within 72 hours. At study end disable enrollment, revoke all codes,
freeze analysis inputs, remove public DNS/ports, rotate secrets and destroy
services/volumes after approved exports and backup retention expire.
