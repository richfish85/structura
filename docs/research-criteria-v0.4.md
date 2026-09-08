# Research Criteria v0.4 — Product Purpose and Measured Difference

Status: **approved for the 1998 pilot; visual presentation deferred**.

## What

Each candidate page may include two evidence-backed research sections:

1. **Why it existed** — the problem, target user, and engineering response attributed to a source.
2. **What difference it made** — benchmark observations whose provenance and test configuration remain inspectable.

These are non-canonical enrichment claims. They do not replace identity, timing, normalization, audit, or human review.

## Why

A specification list cannot explain why apparently similar products existed or whether a changed feature mattered. Purpose and performance also invite overclaiming: marketing positioning can be mistaken for private corporate intent, while benchmark numbers from unlike systems can be made to look comparable. The pilot preserves those boundaries explicitly.

## How

### Purpose claims

Every purpose claim records:

- `claim_scope`: `manufacturer_stated`, `independently_interpreted`, or `inferred`
- the problem addressed
- the target user
- the engineering response
- confidence, source, locator, evidence note, limitations, and researcher

`manufacturer_stated` means the source documents public positioning. It does not establish the manufacturer's complete internal motive. An inferred commercial strategy must remain `inferred` even when plausible.

### Benchmark observations

Every benchmark observation records:

- a `comparison_group_key`
- benchmark and metric names
- numeric result, unit, and direction
- full-enough system configuration to judge comparability
- test date and result provenance
- confidence, source, locator, limitations, and researcher

Allowed provenance values are:

- `standards_body_vendor_submitted`
- `independent_contemporary`
- `manufacturer_claim`
- `reproduced`

Only observations with the same comparison-group key, benchmark, metric, unit, direction, and materially equivalent configuration may be directly compared. A shared product family, clock rate, publication, or benchmark name alone is insufficient.

Missing benchmark evidence is displayed as a gap, not converted into an estimated result. Theoretical clock ratios and manufacturer "up to" claims must not be presented as reproduced performance.

### Pilot boundary

The 1998 pilot remains a launch cohort across CPU, GPU, and HDD. A qualifying record requires evidence of a new product introduction or first commercial shipment during 1998. Products merely remaining on sale are excluded. Desktop, mobile, workstation/server, and approved upgrade segments remain separately labelled; embedded and OEM-only boundary questions remain reviewable.

### Human review

These new sections do not promote a candidate. Human review must still resolve identity, event timing, family-versus-variant boundaries, contradictions, and whether the evidence is strong enough for canonical use.

When an unknown remains useful rather than disqualifying, record an append-only `L0`-`L4` discrepancy decision instead of deleting or silently rewriting the candidate. `OL` marks a deferred omission lead and is not a candidate discrepancy level. See `discrepancy-legend-v0.1.md`.
