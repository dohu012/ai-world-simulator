# ADR-015: Offline Return and Safe Notification Architecture

Status: Accepted, 2026-07-28

## Decision

Use a deterministic, owner/time/source-filtered causal compiler and the existing
PostgreSQL fenced/outbox pattern as the intended durable architecture. In-site
inbox semantics are baseline. Use a repository-native App Router manifest and
minimal same-origin service worker. External Web Push and email remain disabled
until separate live security/browser evidence passes.

Code alone owns eligibility, category, followed-Agent relevance, priority, daily
caps, quiet hours, pause, expiry, channel, copy rejection, and lock-screen
redaction. Model prose cannot expand the allowlisted claim set. Physical device
display is at-least-once provider behavior, never claimed exactly once.

Frozen maxima are six in-site items and two push attempts per owner-local day;
defaults are four and one. Defaults are in-site enabled, push disabled, 22:00–08:00
quiet hours, no automatic permission request, and aggregation into one summary
item per interval/source watermark. High fictional priority never bypasses caps
or quiet hours.

## Consequences

The complete no-push path costs zero model/provider calls and remains usable when
permission is unsupported, denied, revoked, expired, or the provider is down.
`LISTEN/NOTIFY` may later reduce polling latency but cannot become durable truth.
Push endpoints/keys must be encrypted or protected at rest and returned nowhere;
this slice intentionally stores none.

Rollback removes the return-loop route/panel/manifest/worker and policy contracts
without affecting authoritative simulation. The source-level worker kill switch
prevents display during rollback.

