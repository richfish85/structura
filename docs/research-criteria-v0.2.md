# Research Criteria v0.2 — After CPU Normalization and Audit

Status: **candidate criteria for human review**. The 1998 launch-cohort boundary is locked; the segment and granularity rules below are not yet canon.

## What

This revision turns the first CPU verification, normalization, and audit results into repeatable research gates. It preserves the ten-row batch as a pipeline pilot while making incompleteness measurable.

## Why

The audit found no confirmed duplicate identities, but it showed that a supported record set can still be materially incomplete. It also demonstrated that family, speed-grade, cache-configuration, mobile, and upgrade products cannot be handled honestly by a single flat “CPU released in 1998” label.

## How

### 1. State the population before dispatch

Every category batch must explicitly include or exclude:

- desktop, mobile, server/workstation, embedded, and upgrade products;
- OEM/component, boxed/retail, and system channels;
- geographic limits;
- family records, model variants, configuration variants, and orderable SKUs;
- manufacturers and source indexes searched.

An unspecified segment is `unresolved`, not silently included or excluded.

### 2. Keep entity granularity explicit

Each record must declare one current granularity: `family`, `model_variant`, or `sku_unresolved`. A family and its variants may coexist, but reports must not count them as equivalent units. Parent links are proposals until human review.

### 3. Attach dates to typed events

Every date must retain its event: introduction, first shipment, volume shipment, system availability, component availability, or boxed availability. A family event must not be copied to a variant. Announcement alone remains insufficient unless the human-reviewed cohort policy explicitly accepts it.

### 4. Preserve evidence precision

Allowed proposal precision is exact, month, quarter, year, range, or unknown. Quarter values such as `1998-Q3` remain quarters; they are not converted to invented days or months. Canonical product-event storage must support the same distinction before promotion.

### 5. Preserve identity-bearing wording

Suffixes and configuration labels such as `300A`, cache size, mobile, Xeon, and OverDrive must survive normalization. A frequency is a model label, not proof of an orderable SKU.

### 6. Separate leads from candidates

An omission audit creates proposed keys and source leads only. Each lead must pass a new scout and independent verification job before joining the human-review queue. The auditor must not verify its own leads.

### 7. Make completeness claims bounded

A batch may be called complete only relative to its declared manufacturers, segments, event rule, source coverage, and stopping rule. Until those are explicit, use “sample” or “pipeline pilot,” not “census.”

## Current human-review questions

1. Are mobile CPUs included in the first CPU launch cohort?
2. Are upgrade processors included?
3. Do unresolved Xeon cache options become configuration variants, SKU records, or one family placeholder?
4. Should family records appear in public counts alongside variants, or in a separate family count?
5. Which typed event controls year navigation when multiple qualifying events exist?

## Current audit queue

The audit produced nine omission findings representing twelve proposed keys. They cover additional Intel Pentium II, Pentium, Celeron, Xeon, OverDrive, mobile Pentium II, AMD-K6-2, and mobile AMD-K6 products. They remain leads, not cohort members.
