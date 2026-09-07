# Normalization Proposal 03 — 1998 CPU Launch Cohort

## What

This proposal maps exactly the ten verified CPU launch-cohort candidate keys to reviewable display names, manufacturer labels, product granularity, parent links where the batch contains a supported parent, categories, and qualifying launch-event dates. It is a proposal for human review, not a database import or canonical approval.

## Why

The verification pass supports inclusion but deliberately leaves family/model/SKU and channel-availability distinctions open. Normalization must make the records usable without erasing those limits.

## How

- The manufacturer display labels are `Intel` and `AMD`; their raw corporate names remain in the scout hand-off.
- `CPU` is a proposed category label only. The present ontology provides the `category` entity type but has no approved CPU category entity, so this does not create one.
- Exact dates are proposed only for qualifying events explicitly dated in verification. Celeron 266 uses the exact product-introduction date, not a guessed commercial-availability date. Xeon 400 uses the exact family-introduction/component-availability date, not a boxed date.
- AMD-K6-2 350 and 400 use `1998-Q3` and `1998-Q4` with `quarter` precision. These retain source precision and are deliberately not compatible with the current `product_details.date_precision` check; they need typed-event/date-precision schema work before any import.
- The AMD-K6-2 family remains a family record. The 350 MHz and 400 MHz records point to that existing candidate as model variants; the May 28 family date is not inherited by either.
- Celeron `300A` remains `300A` in the display name. It is not normalized to `300`.
- Pentium II Xeon 400 is one `SKU-unresolved` record. Its two cache options are not split or treated as one fully specified SKU.

## Validation

- CSV header matches the agreed 15-column intake order exactly.
- CSV has 10 data rows for the 10 scout candidate keys.
- Every scout candidate key appears once; no unlisted candidate appears.
- `candidate_key` values are unique.
- The only populated `parent_candidate_key` values are `amd-k6-2-family` for the 350 MHz and 400 MHz AMD-K6-2 variants; that parent exists in the same ten-key cohort.

## Open Questions

1. Add typed product-event rows before importing date values that have different introduction, component, system, boxed, and shipment meanings.
2. Extend permitted date precision to include `quarter`, or model quarters as explicit bounded ranges.
3. Decide whether Xeon cache options become configuration variants or orderable SKU records after independent SKU evidence is available.
4. Decide whether the normalised manufacturer labels should be company entities, aliases, or presentation-only fields before canonical import.
