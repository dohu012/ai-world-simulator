# TASK-023 playtest privacy threat model

The study boundary accepts opaque, study-local access codes and bounded option
codes only. It does not require account identity, name, email, IP retention, full
user agent, fingerprint, free text, Oracle text, memories, prompts, vectors, push
endpoints, or narrative exports.

Threats and controls:

| Threat | Control |
| --- | --- |
| forged or shared assignment | server-derived assignment bound to protocol hash; indistinguishable access errors |
| consent replay | version/hash, nonce/idempotency and one active state |
| cross-participant correction | participant/period foreign keys and server scope |
| private/future source leakage | identical allowlisted source set and watermark before render |
| response in logs | request logger records route/status only; response bodies and option payloads forbidden |
| withdrawal race | withdrawal fences reminders and analysis before acknowledgement |
| small-cell reidentification | suppress all branch breakdowns below five included rows |
| study affecting the world | separate tables/API; no imports from study into observations, memories, decisions or ticks |
| malicious Unicode/HTML | enumerated codes, bounded strings, React escaping and strict CSP |
| stale report | protocol/dataset/input watermark must match at promotion |
| backup residue | 30-day backup window disclosed; deletion ledger reconciled after restore |

Kill switches stop enrollment and reminders independently. Withdrawal/deletion
remains available while analysis is disabled. A public deployment must use TLS,
same-origin sessions, CSRF/origin checks, rate limits, no third-party scripts,
`Cache-Control: no-store`, isolated admin routes and a rotated session secret.
