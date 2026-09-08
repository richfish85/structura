# Expanded CPU audit notes

## Scope

This is an immutable audit of the original ten CPU candidates plus twelve independently verified omission candidates. It covers 22 frozen keys. It does not create candidates, normalize, approve, merge, promote, or write to SQLite.

## Key outcomes

- The Intel 350/400 Pentium II pair, Celeron 300/300A pair, and mobile Pentium II 233/266 pair remain distinct speed-grade records.
- The two OverDrive output keys are a high-severity structure issue: Intel describes one physical product with two compatibility/output mappings. A human must decide whether to retain two provenance rows under one product record or establish separate product evidence.
- AMD-K6-2 family and variants are intentionally mixed granularity. Family timing and quarter timing are not interchangeable; no AMD variant receives invented exact precision.
- Xeon 400 cache configurations remain unresolved at SKU granularity. Xeon 450 remains a product-announcement-plus-planned-shipment boundary case.
- The Intel chronological register's 1998 entries are represented by the expanded Intel keys. AMD completeness remains open because no equivalent complete AMD register was in the frozen evidence.

## Validation

- `audit.csv` uses the exact 13-column `AUDIT_COLUMNS` contract with standards-compliant CSV quoting.
- 13 unique finding IDs use approved finding types, severities, and dispositions.
- All affected keys are among the 22 frozen candidate keys.
- No proposed candidate key was created; the residual omission finding deliberately records an evidence-boundary risk only.
- No database or canonical write occurred.

## Required human review

1. Decide whether the two OverDrive output rows should be restructured as one product plus compatibility assertions.
2. Decide whether Xeon 450's announced product and planned 1998 two-way-system shipment satisfy the qualifying-event policy.
3. Keep AMD speed grades at quarter precision and declare a future AMD-only stopping rule before calling the cohort complete.
