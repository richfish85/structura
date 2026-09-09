# 1997 Launch-Cohort Pilot — Status

Current status (2026-09-09): **coordinator audit repairs imported in the unified build; no canonical records**

The 2026-09-08 checkpoint below is preserved as historical context; its repair blocker and zero audit counts are superseded by the update at the end.
Access/reconciliation date: 2026-09-08

## What

This bounded pilot applies the Structura workflow to a representative 1997 launch cohort across CPU, GPU, and HDD slices. It currently contains 9 CPU, 6 GPU, and 5 HDD scout candidates.

## Why

1997 tests an earlier hardware generation while preserving the same boundaries used for 1998: product identity, family/model granularity, chip-versus-board distinction, introduction versus production versus shipment, channel scope, source provenance, and explicit omission leads.

## How

- CPU, GPU, and HDD scouting were run as separate lanes with frozen candidate and source registers.
- Each lane records official or contemporary evidence, unknowns, omission leads, and manifest hashes.
- Independent verification is now being performed over the frozen outputs.
- Normalization, audit, purpose/benchmark context, discrepancy review, SQL import, and HTML rendering follow only after verification succeeds.

## Pilot boundary

The qualifying event is a new product introduction or first commercial shipment during calendar year 1997. Announcement, sampling, planned production, OEM-only timing, and later retail availability remain distinct event claims. This is not a worldwide census.

## Current counts

| Slice | Scouted | Independently verified | Normalized | Context researched | Audited |
|---|---:|---:|---:|---:|---:|
| CPU | 9 | 9 | 9 | 9 | 0 |
| GPU | 6 | 6 | 6 | 6 | 0 |
| HDD | 5 | 5 | 5 | 5 | 0 |
| **Total** | **20** | **20** | **20** | **20** | **0** |

## Deferred

Visual presentation, benchmark bars, and granular census expansion remain deferred. The three audit packets need CSV repair before their findings can be imported; omission leads remain preserved as research pointers rather than silently added to the candidate set.


## 2026-09-09 — Audit repair and unified build

New coordinator copies under `research_batches/coordinator/1997-audit-repair-20260909/` repair the three audit handoffs. Original worker artifacts remain unchanged. Each copy has a repair manifest containing source/output hashes and field-level changes.

Unsupported finding-type spellings are mapped to the existing intake vocabulary without changing disposition or author. Resolved scope checks retain `resolved_no_change`; the mapped scope-error machine category is not a newly discovered defect. HDD finding `hdd-aud-002` also had shifted semantic fields: the PC Watch URL, report locator and evidence note are restored to their proper columns.

The unified build successfully imports 20 audit rows (CPU 9, GPU 6, HDD 5), alongside 20 candidates, 20 verification records, 20 normalization proposals and 20 context claims. This verifies packet intake; it does not resolve the underlying findings or make the records canonical. The explorer now includes this cohort. Census expansion remains deferred.
