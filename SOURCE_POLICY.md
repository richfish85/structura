# Structura source policy

Every imported claim remains provisional until its evidence, identity, scope, and review history satisfy this policy. Hashes prove artifact identity, not factual truth.

## Evidence standard

Store the source key, title, publisher/origin, URL or archive URL, publication date when known, access date, source tier, precise locator, evidence role, and a concise claim-specific note. Preserve uncertainty and conflicting accounts. Do not bulk-copy source material.

| Tier | Typical source | Normal use |
|---|---|---|
| 1 | Manufacturer documents, manuals, datasheets, standards bodies, regulatory filings, archived official pages | Preferred evidence for published identity and specifications. |
| 2 | Contemporary technical publications, professional reviews, established databases | Corroboration, market timing, and independent measurement. |
| 3 | Teardowns, repair material, specialist archives, museums | Physical detail and archival support, with provenance and rights considered. |
| 4 | Forums, personal sites, retail listings, general encyclopedias | Leads or context; rarely sufficient alone. |

Tier is not a truth score. Manufacturer claims establish what a manufacturer published; they do not become independent measurements. Repetition of one origin is not corroboration.

Evidence roles are `supports`, `contradicts`, `context`, and `lead_only`. A locator-free source list is not adequate evidence for a material claim.

## Research and normalization

Use the sequence `scout -> verifier -> normalizer -> auditor -> human review`. Context research may enrich a staged candidate but cannot bypass these gates.

- Scout within a declared population and stopping rule; retain raw wording and unknowns.
- Verify identity, category, timing, and scope independently. Do not expand the population or normalize the scout's conclusion.
- Normalize only to existing approved/proposed terms. Preserve raw fields and flag unmapped vocabulary, family/model ambiguity, and date precision.
- Audit frozen artifacts for omissions, duplicates, scope errors, date inheritance, category errors, and weak evidence. Report findings; do not rewrite another worker's artifact.
- Coordinator repairs or merged packets are new artifacts with source/output hashes and explicit changes. Original runs remain immutable.

The same agent must not scout and verify, or normalize and audit, the same record. A model name alone does not establish independence. See `docs/multi-agent-research-protocol.md` for artifact and identity fields; [AGENTS.md](AGENTS.md) controls delegation limits.

## Dates, identity, and claims

- Announcement, sampling, production, shipment, retail availability, and review dates are different events.
- Never infer an exact date from a copyright year, listing, review, forecast, or nearby family event.
- Keep product, model, family, board, chip/component, and configuration identities separate until evidence supports a join.
- Preserve `unknown`, `not found`, `conflict`, and `not applicable` distinctly.
- Compatibility and replaceability require explicit scope. A shared connector or standard name is insufficient.
- Benchmark comparisons require the same named comparison group and visible configuration, provenance, direction, units, and limitations.

## Canonical promotion

Agents may recommend `verified`, `review_required`, or rejection. Only a human reviewer, or a coordinator acting on a recorded human decision, may promote an entity, relationship, source, or ontology term to canonical.

A promotion requires supporting evidence, resolved or explicitly accepted conflicts, the exact object and status change, evidence artifact identities, rationale, reviewer, date, and an append-only review record. Promotion occurs in a separate transaction, followed by foreign-key/integrity checks and regeneration of derived views. Import, verification, normalization, audit acceptance, discrepancy review, or a clean build does not itself promote canon.
