# TASK-023 preregistered protocol

Status: frozen for implementation validation; no included participant has enrolled.  
Protocol: `gray-harbor-product-validation:1.0.0`  
Design: two-period counterbalanced crossover, AB/BA, target 16 completed, minimum 8.  
Separation: 24–72 real hours. One neutral reminder is permitted only after separate consent.

Primary outcome is the paired difference in six coded comprehension items
(source, epistemic class, causal order, correction, decision, outcome). The
predeclared test is superiority: mean paired causal-minus-chronological score of
at least 0.10, with the 95% interval not indicating material harm. The exact sign
test is reported as sensitivity evidence, never as the product rule.

Safety gates: no rating of 5/5 for participant-experienced pressure, anxiety,
guilt, manipulation, or emergency mimicry caused by the interface; median clarity
and usefulness must each be at least 4/5. Fictional-world intensity is a separate
construct. Low ratings are never exclusion reasons.

Inclusion requires versioned consent, both assigned exposures, and at least one
valid comprehension response per period. Predeclared exclusions are duplicate
enrollment proved by the same study-local access code, protocol ineligibility,
technical exposure hash mismatch, or withdrawal. Missing period 2 remains
missing; the participant is not replaced. Results report period, sequence and
carryover sensitivity.

Expansion requires every hard deterministic and human safety gate, at least eight
completed participants, and a bounded probe completed as the first choice by at
least 50% of included participants across both sequences. Otherwise the only
decision is `defer`. Raw text is not collected.

Retention: row-level coded data 30 days after report freeze; deletion SLA 72
hours; aggregate counts are retained only with cells of at least five. Protocol,
formulas and thresholds may only be superseded, never edited after enrollment.

Reproduction:

`cd backend && pytest tests/test_product_validation.py`
