# ADR-017: Small single-host production pilot

Date: 2026-07-31  
Status: Accepted for staging; production enrollment requires owner approval

Use one direct host with Caddy, frontend, FastAPI, PostgreSQL and Redis on an
internal Compose network. Only Caddy publishes ports. Caddy provides TLS and
redacts headers/query strings; `/playtest/admin/*` is denied on the public
origin. Administration uses a private host path and a separate key.

Use pre-issued 192-bit opaque codes, versioned HMAC-SHA256 storage, expiry,
activation and revocation state. Keep enrollment off by default. PostgreSQL
triggers freeze protocol/question content after first enrollment. Use encrypted
custom `pg_dump`, isolated restore, and deletion tombstones. Use bounded local
health/capacity monitoring; no hosted analytics, replay, tracing or identity
provider.

The API enforces trusted hosts, HTTPS-only CORS when production enrollment is
enabled, 32-byte minimum admin/pepper secrets, neutral errors and Redis limits
keyed by code HMAC rather than IP. Next is locked to 15.5.22 with audited
PostCSS/Sharp overrides; the final full npm audit reports zero vulnerabilities.

This architecture is removable by tearing down the pilot Compose project,
revoking secrets/codes, retaining only approved aggregates and expiring encrypted
backups. It is not a general production platform. Kubernetes, Vault, external
identity, tunnels, Push/email/SMS, PITR and hosted monitoring remain deferred.
