# Research Criteria v0.3 — CPU Segment Boundary

Status: **mobile and upgrade boundaries approved; remaining criteria are candidates for human review**.

## What

This revision applies the human boundary decision made after the CPU normalization and omission audit. The 1998 CPU launch cohort includes desktop, mobile, server/workstation, and upgrade processors.

## Why

The launch-cohort definition is based on qualifying product introduction or first commercial shipment, not on one market segment. Excluding mobile or upgrade products would hide legitimate launches and make completeness claims ambiguous.

## How

### 1. Included segments

- Desktop
- Mobile
- Server/workstation
- Upgrade

Each record must retain its segment. Reports must show separate segment totals before any explicitly labelled all-segment roll-up.

### 2. Still-unresolved segments

Embedded and OEM-only processor boundaries remain unresolved. Researchers may record them as audit leads but must not add them to this cohort without another human boundary decision.

### 3. Entity granularity

Each record declares `family`, `model_variant`, or `sku_unresolved`. Family and variant records may coexist, but they are never counted as equivalent units. Configuration labels, cache sizes, mobile designations, upgrade designations, and identity-bearing suffixes remain visible.

### 4. Event and precision

Every date remains attached to its evidence event. Family dates are not inherited by variants. Exact, month, quarter, year, range, and unknown precision remain distinct; quarter evidence is never converted into an invented exact date.

### 5. Omission-lead gate

The twelve approved-scope omission keys still require fresh scouting and independent verification. Audit evidence alone does not create a candidate or canonical record, and the auditor must not verify its own leads.

## Remaining human-review questions

1. Do unresolved Xeon cache options become configuration variants, SKU records, or one family placeholder?
2. Should family records appear in public counts alongside variants, or in a separate family count?
3. Which typed event controls year navigation when multiple qualifying events exist?
4. Are embedded and OEM-only processors in scope for this cohort?
