# Audit Report 04 — 1998 CPU Launch Cohort

## What

This independent Luna audit checked the ten existing CPU records for duplicate identities, family/variant overlap, unsupported date inheritance, category/scope errors, and credible omission leads. It does not add any lead to the cohort, normalize names, change shared status, or promote records.

## Why

The verification pass established that all ten sampled records have primary-source support, but it deliberately did not test whether the Intel/AMD sample was complete. This audit tests that boundary before human review.

## How

### Audit boundary

The audit began with all ten rows in `01_scout_candidates.csv`, their eight registered primary sources, and `02_verification.csv`. It then searched authoritative first-party sources for Intel and AMD CPU introductions or first commercial shipments explicitly situated in calendar year 1998. The search covered:

- Intel's official 1998 processor chronology;
- Intel's archived 1998 product press-release index/results for desktop, mobile, server/workstation, and upgrade products;
- AMD's 1998 filed press-release exhibits and 1998 annual-report evidence already registered in the batch.

The audit did not attempt a complete all-manufacturer CPU census, retail listings, secondary review sweep, part-number enumeration, or GPU/HDD audit. It did not treat the official chronology alone as final proof where a contemporary product source is needed.

### Stopping rule

Stop when each sampled record has been checked for duplicate/family overlap and date inheritance, and the official Intel chronology plus the registered AMD Q3/Q4 filings have been traversed for named 1998 CPU introductions absent from the sample. Newly located names are recorded as leads only. Further research belongs to independent scout/verifier jobs.

## Findings

The machine-readable findings are in [`04_audit_findings.csv`](04_audit_findings.csv).

- 15 findings total.
- 6 structural findings on the existing records or batch boundary.
- 9 omission-lead findings.
- 0 duplicate identities confirmed.
- 2 family/variant or configuration-granularity issues require human review.
- 1 scope-gap finding: the sample is not complete across mobile, upgrade, and additional speed-grade products.
- 9 findings remain `open` as lead-only proposals; none is an accepted cohort record.

### Existing-record audit

The Pentium II 350/400 and Celeron 300A/333 pairs are distinct named variants, not duplicates. The AMD-K6-2 family alongside its 350/400 variants is a deliberate family/variant overlap, not a duplicate, but it must not inflate a model count or inherit the family date. The Pentium II Xeon 400 record needs a cache-configuration decision because Intel names 512 KB and 1 MB options with separate prices. The current verification correctly avoids unsupported date inheritance; this remains an import guardrail.

### Omission leads

The sample is materially incomplete under the current CPU scope. Credible first-party leads include Intel Pentium II 333, Pentium 266, mobile Pentium II 233/266/300, Celeron 300, Pentium II Xeon 450, and Pentium II OverDrive 300/333. AMD's filed Q4 release also names AMD-K6-2 366 and 380, and its Q3 release names a mobile AMD-K6 300. These are proposed keys only and require separate scout/verifier work.

## Disposition

No record is removed or added. Existing records stay in the human-review queue with the structural flags above. Omission leads should be scheduled as new, independently verified jobs after the cohort's mobile/upgrade inclusion boundary is explicitly decided. The auditor identity is `intel-luna-audit-01`; this lane must not verify or normalize its own leads.

## Risks left

- The official chronology may omit obscure, regional, OEM-only, or embedded products.
- “Introduced” is not always the same as first shipment or boxed availability; leads retain their source event wording.
- The Intel and AMD evidence is first-party and therefore not independent market corroboration.
- Several proposed keys may resolve into family/variant/SKU structures rather than one row each.
