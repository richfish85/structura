# 1998 Launch-Cohort Pilot — Status

Status: **research workflow complete; human review required; no canonical records**  
Access/reconciliation date: 2026-09-08

## What

The bounded 1998 pilot now covers three review slices:

| Category | Candidates | Independently verified | Normalization proposals | Purpose claims | Comparable benchmark observations | Audit findings |
|---|---:|---:|---:|---:|---:|---:|
| CPU | 22 | 22 | 22 | 22 | 6 | 28 across initial and expanded audits |
| GPU | 8 | 8 | 8 | 8 | 0 | 17 |
| HDD | 4 | 4 | 4 | 4 | 0 | 11 |
| **Total** | **34** | **34** | **34** | **34** | **6** | **56** |

All 34 records remain candidates. “Complete” means the declared pilot workflow has been completed for the bounded candidate set; it does **not** mean every CPU, GPU, or HDD sold or launched worldwide in 1998 has been enumerated.

## Why

The pilot tests whether Structura can preserve identity, timing, category boundaries, stated product purpose, comparable performance evidence, contradictions, and omission leads from parallel research without silently promoting claims.

## How

- Scouts created frozen candidate and source registers.
- Different researchers independently verified each GPU/HDD set; the expanded CPU candidates were also independently verified.
- A separate normalizer proposed entity granularity, names, timing precision, and qualifying events.
- Auditors recorded duplicates, boundary problems, evidence gaps, and omission leads without adding candidates.
- Context research added “Why it existed” evidence for every candidate or an explicit gap.
- Only one benchmark comparison survived the comparability gate: six SPEC CPU95 observations covering Celeron 300, 300A, and 333 across two same-platform metric groups.
- SQLite remains authoritative; the plain HTML export is derived and read-only.

## Human-review decisions

1. **Pentium II OverDrive identity:** the two frozen 300/333 output keys appear to describe one physical upgrade product with two input/output mappings.
2. **Pentium II Xeon 450 event:** evidence establishes an announcement and planned October system shipment, not an unambiguous completed introduction/shipment event.
3. **Quantum Fireball EL event:** May mass production is supported, but first commercial shipment is not established.
4. **GPU timing:** MGA-G200 is announcement-only; RAGE 128 production timing is conflicting/forecast; Banshee card availability is forecast rather than confirmed.
5. **Expansion boundary:** GPU and HDD audits retain proposed-only omission leads. They require fresh scouting and verification if the pilot is expanded toward a census.

## Integrity corrections caught during intake

- The GPU audit initially used unapproved ontology labels; the importer rejected it and the run was corrected.
- GPU/HDD purpose rows with malformed comma quoting were rejected and regenerated.
- Eleven legacy CPU verification rows contained one surplus empty CSV field. The coordinator removed only that empty field, restored the declared limitations/questions/notes mapping, and refreshed the provenance hashes.
- Two HDD verification-note fields contained an unquoted embedded comma. The coordinator quoted those fields without changing their wording and refreshed every dependent provenance hash.

## Deferred

Visual charts, normalized performance bars, and designed presentation remain deliberately deferred. The current export is a utilitarian evidence review.
