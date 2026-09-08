# Discrepancy Legend v0.1

Status: **approved for the 1998 pilot**  
Decision date: 2026-09-08

## What

The discrepancy level describes the strongest unresolved evidence problem attached to a candidate. It is not a product-quality score, performance rating, or reason to delete a useful record.

| Code | Label | Meaning |
|---|---|---|
| `L0` | No material discrepancy recorded | Current sources align at the level being claimed. This does not make the record canonical. |
| `L1` | Bounded detail gap | A qualifying event is supported, but precision such as exact day, channel, region, or SKU remains incomplete. |
| `L2` | Availability not established | Product existence or a plausible qualifying event is supported, while shipment or commercial availability is unknown, manufacturer-stated, or forecast-only. |
| `L3` | Identity or cohort boundary open | Product granularity, one-product-versus-many identity, or whether the evidenced event meets the cohort rule remains unresolved. |
| `L4` | Material source conflict | Sources materially conflict or cannot distinguish competing interpretations. No disputed value should be silently selected. |

`OL` is a separate **deferred omission lead** marker. It identifies a possible missing candidate that has not passed scouting and verification. It is not a discrepancy level and does not affect the accepted pilot records.

## Why

The pilot retains useful hardware records even when one fact remains uncertain. The legend makes the uncertainty visible and reusable for later filtering or visualization without collapsing identity, timing, and source conflicts into a single confidence score.

## How

- Display the latest reviewed level with the candidate and retain the explanation and resolution threshold.
- Keep all underlying verification and audit findings visible.
- Treat the level as the highest material unresolved state, not as an average.
- Never infer exclusion from `L1` through `L4`; disposition is a separate decision.
- Never infer canon from `L0`; canonical promotion remains a separate human gate.
- Change a reviewed level only through a dated review decision that identifies the evidence and reviewer.
- For a future contribution workflow, retain contributor identity or relationship, the exact claim, documentary attachment or source, permission/provenance, the affected field, and the independent review outcome.

## Visualization note

The codes are stable data labels. Future colours, icons, or filters may represent them, but presentation must preserve the textual label and must not rely on colour alone.
