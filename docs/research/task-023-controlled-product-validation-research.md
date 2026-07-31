# TASK-023 controlled product-validation research

Research date: 2026-07-30. The comparison covered repository-native assignment,
GrowthBook, Unleash, Flagsmith, PostHog, Matomo, Plausible, OpenTelemetry,
LimeSurvey, Formbricks, KoboToolbox, SurveyJS, Python standard library,
SciPy/statsmodels, Playwright and axe-core. Version/license decisions and removal
seams are frozen in ADR-016.

The repository-native spike won because this study needs at most 16–32
participants, exact replay from coded exports, source fencing and deletion—not
engagement optimization. Its event schema cannot represent narrative bodies,
identifiers are study-local, and the entire analysis is a pure function.

The crossover keeps power efficient but requires period/order reporting and
matched non-identical intervals. Exact sign and Wilson intervals are suitable
small-sample sensitivity summaries. A p-value is not the gate: practical margin,
safety, sample class and concrete demand are all mandatory.

Causal and chronological variants must contain identical authorized source
tuples. The corpus includes reject, partial-follow, correction, irreversible
outcome and privacy decoys. The causal view may change grouping and labels, never
facts. Model prose remains rejected.

Accessibility research applies WCAG 2.2 keyboard, focus-visible, status,
reflow/320px, zoom, contrast and reduced-motion expectations. Automated scans do
not establish screen-reader usability; the protocol requires documented manual
keyboard and screen-reader review before enrollment.

Deployment selection is local same-device facilitation. Docker Compose/LAN HTTPS
remain viable for a later approved pilot; Cloudflare Tunnel, ngrok and public
cloud are rejected until access-code, TLS, log, backup, teardown and incident
response evidence exists. Estimated incremental provider/model cost is zero.
