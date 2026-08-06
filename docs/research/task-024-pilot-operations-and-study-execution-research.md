# TASK-024 pilot operations research

Accessed 2026-07-31. This is a deployment decision record, not evidence that a
public pilot or human study ran.

| Area | Candidates reviewed | Selection and reason |
| --- | --- | --- |
| TLS/proxy | Caddy 2.11.4 (Apache-2.0), nginx, Traefik; Cloudflare Tunnel, Tailscale, ngrok; direct cloud; LAN | Caddy on a direct small host: smallest automatic-HTTPS configuration and clean removal. Tunnels and hosted edges are deferred because IP/region/retention terms add a processor. LAN is staging-only. |
| anonymous access | native codes, signed cookie, Authentik, Keycloak, Ory, Auth0/Clerk/Supabase | Native HMAC-hashed, expiring, pre-issued codes. The identity products require accounts or an unnecessary identity store. |
| secrets | injected env, Docker secrets, SOPS/age, Bitwarden SM, Vault | deployment-injected environment file with restrictive host permissions for this single-host pilot; SOPS/age is next choice if more than one operator. Never image/Git. |
| supply chain | lockfiles, pip-audit, npm audit, OSV, Trivy/Grype, Syft/CycloneDX, Cosign | existing lockfile plus pip-audit/npm audit, Trivy and Syft at deployment freeze. Record immutable image digests then; do not claim the mutable tags are frozen. |
| backup | pg_dump/restore, pgBackRest, WAL-G, managed backup, restic/Borg | PostgreSQL 18.4 matching the measured server, encrypted custom-format `pg_dump`, isolated `pg_restore`, separately retained deletion tombstones. PITR systems are disproportionate for <=32 participants. |
| monitoring | bounded native counters, OTel, Prometheus/Grafana, Loki, Sentry/GlitchTip, hosted suites | local health/capacity counters and redacted Caddy logs. No row data, headers, query strings, IP export, replay, or hosted error processor. |
| accessibility | Playwright+axe, Pa11y, Lighthouse, Accessibility Insights, Narrator/NVDA, VoiceOver | existing Playwright plus axe, manual keyboard/zoom/forced-colors/reduced-motion and Windows Narrator. Firefox/Edge manual; WebKit is automation only unless macOS hardware is recorded. |
| recruitment | direct internal, community, Prolific, calendar/survey SaaS | direct separately scheduled recruitment. Contact/compensation records remain outside the app with no exported join key. Prolific/community are deferred pending processor and coercion review. |
| analysis | repository stdlib, SciPy/statsmodels, independent R/Python | frozen repository implementation plus a separately reviewed golden Python script before enrollment. No outcome rule changes after enrollment. |

Measured repository spike: a 32-byte URL-safe code contains at least 192 random
bits; only HMAC-SHA256 is stored; an expired/revoked/unissued code is rejected;
the second presentation is fenced for 24 hours; custom-format backup and
deletion reconciliation have scripts. A PostgreSQL 17 client correctly refused
to dump the measured PostgreSQL 18.4 server; the deployment was upgraded to an
18.4 client/server and a 338,112-byte custom archive was generated. Local unit
tests pass. TLS renewal,
TLS, API/frontend image build and screen-reader review remain unexecuted until an
approved staging host and working registry path exist. Restore, deletion
reconciliation, fresh migration round trip and 32-concurrent activation passed.

On 2026-08-03 npm audit initially identified high findings in Next's PostCSS and
Sharp paths plus development brace-expansion. Next was patched within major 15
to 15.5.22; overrides lock PostCSS 8.5.25 and Sharp 0.35.3; the non-forced audit
fix updated brace-expansion. Full and production-only npm audits then reported
zero vulnerabilities, and the full frontend build/test gate passed.

Docker Scout scanned local `postgres:18.4-alpine` digest `9a8afca54e78` on
2026-08-03 and found 1 critical/16 high vulnerabilities, all attributable to Go
1.24.6 in `/usr/local/bin/gosu`; fixed Go versions exist but the current official
PostgreSQL image has not incorporated them. Scout reports the Alpine base itself
as 0C/0H. The image is rejected for public enrollment until upstream rebuild and
clean rescan; removing the privilege-drop binary is not an acceptable workaround.

Sources: Caddy upstream release and automatic HTTPS documentation
(`github.com/caddyserver/caddy`, latest 2.11.4); PostgreSQL 17 `pg_dump` and
backup/restore documentation (`postgresql.org/docs/17`); OWASP Authentication,
REST Security and Bot Management cheat sheets; Playwright accessibility testing
documentation and axe-core upstream. Licenses and hosted terms must be
rechecked at the production freeze.
