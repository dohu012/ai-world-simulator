# TASK-022 Threat Model

- Cross-owner, future, invisible, or private sources: reject before compilation;
  source owner/world/time and immutable hash are mandatory.
- Prompt/copy injection: model output has no policy authority; bounded extractive
  claims pass the prohibited-copy taxonomy.
- Endpoint/key leakage: no subscription is persisted or serialized in this
  disabled-push slice; future adapters must expose opaque IDs only.
- Forged caller/CSRF: established server-derived demo identity is mandatory;
  mutation endpoints require the same-origin CSRF token and allowlisted codes.
- Manipulation: reject guilt, sentience/dependence, blame, fake emergency,
  countdown, permission pressure, and quiet-hour pressure in English and Chinese.
- Replay/analytics leakage: instrumentation accepts only declared event codes;
  never narrative bodies, keystrokes, DOM, IP, user-agent, vectors, or prompts.
- Service-worker compromise/update: no third-party imports or cache; same-origin
  navigation only; `PUSH_ENABLED` is the kill switch.

