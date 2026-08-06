# TASK-024 public pilot threat model

Protected assets are consent, assignment, bounded answers, correction history,
deletion choices, the frozen corpus and report hashes. Names, email, phone, raw
IP, full user agent, free text, narrative input and model calls are forbidden.

| Threat | Control | Stop condition |
| --- | --- | --- |
| code guessing/sharing | >=192-bit random pre-issued code, HMAC storage, expiry, neutral errors; proxy rate limit required before public opening | access or enumeration evidence |
| code/log leakage | header-only code; Caddy deletes headers/query; no URL code; no-store | code in any log/export |
| protocol tampering | enrolled-protocol/question database triggers; artifact hash freeze | mutation or wrong hash |
| premature period 2 | server-side 24-hour fence | early exposure |
| cross-owner access | code maps to one participant; all writes use authenticated owner id | any cross-owner row |
| restore resurrection | deletion tombstones applied after isolated restore | deleted active row |
| admin exposure | public proxy returns 404 for admin prefix; private administration only | public report/code issue route |
| participant-to-world flow | study tables/service remain disconnected from world/agent inputs | any world/Agent mutation |
| abusive traffic | connection/body limits and generic 429 at proxy; counters contain no IP | availability or privacy breach |

Residual risks: the host and database operator can access row data; backups retain
deleted rows until expiry; a shared raw code permits shared access; Caddy's local
access log sees connection metadata even though it is not exported. Disclose
these limitations and stop enrollment on any listed failure.
