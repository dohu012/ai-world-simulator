# TASK-022 Offline Return and Notification Research

Access date: 2026-07-28. This research precedes dependency selection.

## Measured decision matrix

| Candidate | Version/activity/license | Result and decision |
|---|---|---|
| Next.js native manifest/service worker | Next.js official App Router guide, updated 2026-03-25; framework already pinned by this repository | Accept manifest and repository-owned worker. Smallest removal seam; no runtime dependency. HTTPS and real browsers remain deployment gates. |
| Serwist | Not installed; third-party worker/build abstraction | Defer. The slice needs no caching recipe and the native worker is inspectable and kill-switchable. |
| W3C Push/Notifications APIs | Push API WD 2025-12-01; standards documents | Accept as capability boundary only. Permission does not imply category consent; endpoint metadata remains sensitive. |
| `web-push` / `pywebpush` | `pywebpush` 2.3.0, MIT, installed 2026-07-29 | Accept the Python provider adapter boundary because it fits the FastAPI runtime and Web Push encryption/VAPID standards. Live delivery remains disabled until a disposable subscription exists. |
| PostgreSQL outbox + `SKIP LOCKED` | Existing PostgreSQL architecture | Accept durable truth. Unique logical keys and fencing cover two-worker claims; provider work must occur after commit. |
| PostgreSQL `LISTEN/NOTIFY` | PostgreSQL 18 official docs | Defer as wake hint only: notifications are transaction-sensitive and not durable job truth. |
| Redis Streams/PubSub, Celery, Temporal | Existing Redis is non-authoritative; other dependencies absent | Reject/defer for this slice. They add operational state without proving a failure in the existing fenced-job pattern. |
| SSE/WebSocket/bounded polling | Browser-client delivery | Accept bounded polling through existing query client. SSE/WebSocket provide no correctness advantage for a low-volume inbox. |
| Deterministic causal compiler | Repository-owned, `causal-compiler-v1` | Accept. Exact source text with epistemic labels gives claim precision/attribution 1.0 and zero model cost. |
| Model-assisted prose | Provider/model unspecified | Defer. It cannot own eligibility, privacy, priority, or claims; deterministic fallback is complete. |
| Repository-native minimized events | Project code | Accept. Allowlisted event codes only; no raw text, DOM replay, fingerprint, IP, or user-agent persistence. |
| PostHog/Matomo/Plausible/OpenTelemetry | Hosted/self-hosted products not required | Defer analytics adoption. Hosted regions/subprocessors/retention are therefore not introduced into the data path. |
| SMTP/SES/Postmark/Resend/SendGrid | External delivery products | Future adapter only. Email activation, authentication, unsubscribe, bounce, complaint, region, retention, and cost remain a separate ADR. |

## Executable findings

The fixed tests in `test_return_loop_policies.py` exercise cross-owner/future
exclusion, deterministic source watermarks, English/Chinese coercive-copy
rejection, no-push defaults, followed-Agent filters, caps, and timezone/DST-aware
quiet deferral. The compiler performs no provider call and acquires no world lock.

The worker is repository-native, contains no third-party imports or cache, uses a
same-origin fixed click route, redacts lock-screen text, and has a source-level
kill switch (`PUSH_ENABLED = false`). This is deliberately not evidence that live
Web Push passed: subscribe, expiry, provider receipt, and browser-matrix tests are
blocked without deployment HTTPS, VAPID secrets, and consented disposable
subscriptions. Push therefore remains disabled rather than being claimed complete.

Playwright 1.62.0 was added as a development-only browser harness. Managed browser
downloads timed out; the installed stable Google Chrome channel passes the
no-push/service-worker/permission tests. Firefox and WebKit remain unverified.

Sources: [Next.js PWA guide](https://nextjs.org/docs/app/guides/progressive-web-apps),
[W3C Push API](https://www.w3.org/TR/push-api/),
[MDN Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API),
[PostgreSQL NOTIFY](https://www.postgresql.org/docs/current/sql-notify.html).
