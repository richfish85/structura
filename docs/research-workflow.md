# Research Workflow

## What

Research moves through separate discovery, verification, normalization, audit, and human-review stages. No automated researcher owns a record end-to-end.

## Why

Separating stages reduces the chance that one mistaken assumption becomes a polished canonical record. The workflow also keeps omissions, conflicts, and uncertainty reviewable.

## How

```text
Scout -> Verifier -> Normalizer -> Auditor -> Human review -> Canonical SQL
```

Purpose and benchmark research is a parallel enrichment lane. It may begin once a candidate identity is staged, but it never bypasses the main gates:

```text
staged candidate -> purpose / benchmark evidence -> human review
```

### Scout

Find candidate products within a bounded year and category. Record raw manufacturer/product wording, model number, timing claims, sources, and notes. Do not infer missing dates or compatibility.

### Verifier

Check identity, manufacturer, release timing, and category independently. Add sources and flag conflicts. Do not expand the census or normalize away uncertainty.

### Normalizer

Map verified wording to approved entity types, predicates, category terms, and manufacturer identities. Do not invent vocabulary; flag unmapped terms.

### Auditor

Look for omissions, duplicate identities, inconsistent naming, category errors, suspicious dates, and weakly supported records. Report findings without changing the dataset.

### Context researcher

Record what problem a source says the product addressed, who it targeted, the engineering response, and any defensibly comparable benchmark observations. Distinguish manufacturer positioning from independent interpretation and inference. Never put unlike benchmark configurations in the same comparison group, and record a gap when no comparable result survives review.

### Human review

Resolve material ambiguity, approve ontology changes, and decide whether a record advances. Human decisions are append-only: they add a discrepancy level, disposition, rationale, and the evidence that could resolve the question without rewriting the underlying agent artifacts. The UI is part of review: browsing the records should reveal categories and relationships that do not feel structurally honest.

The pilot uses the stable `L0`-`L4` discrepancy legend in `docs/discrepancy-legend-v0.1.md`. Levels describe evidence uncertainty, not product quality or database eligibility. `OL` is a separate deferred omission-lead marker, not a candidate level.

## Source hierarchy

| Tier | Typical sources | Use |
|---|---|---|
| 1 | Manufacturer documentation, manuals, datasheets, regulatory filings, standards bodies, archived manufacturer pages | Preferred factual evidence |
| 2 | Contemporary technical publications, professional reviews, established hardware databases | Strong corroboration and market timing |
| 3 | Teardowns, repair documentation, specialist archives, museum collections | Physical detail and archival support |
| 4 | Forums, Reddit, personal sites, retail listings, general encyclopedias | Leads and context; rarely sufficient alone |

Source tier is not a truth score. A primary source may omit an inconvenient fact; an expert archive may preserve information unavailable elsewhere. Contradictions remain visible.

## Initial pilot

Scope: the 1998 launch cohort across CPU, GPU, and HDD categories. A candidate must have evidence of a new product introduction or first commercial shipment during 1998. Products launched earlier and merely remaining on sale are outside this first dataset.

The three categories intentionally stress different modelling problems:

- CPU: families, individual models, sockets, and dates
- GPU: chips versus boards and multiple board manufacturers
- HDD: capacities, interfaces, model families, and regional availability

Compatibility, openness, repairability, scarcity, and market conclusions are outside this first batch.

Announcement-only records and records with unresolved shipment timing remain useful candidates. Their discrepancy level must preserve whether the evidence supports existence, announcement, production, forecast availability, or completed shipment; no later event should be inferred. Channel-specific availability should be preserved rather than collapsed into one date.

The 1998 omission leads are retained as deferred `OL` items. They are not discarded, but granular expansion toward a census is postponed while the representative pilot is reused across other years and categories.
