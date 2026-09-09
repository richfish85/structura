# Structura schema

The executable schema is the ordered SQL in `schema/`. This file is its concise map; when the two disagree, migrations and tests govern runtime behavior, and this document must be corrected.

## Core model

- `schema_migrations`: applied migration identifiers.
- `entity_types`, `predicates`: controlled but currently proposed ontology terms.
- `research_batches`: bounded research populations and workflow state.
- `sources`: resolved source identities, tier, dates, URL/archive URL, and notes.
- `entities`: stable `entity_key`, type, description, record status, confidence, and optional batch.
- `product_details`: model, announcement/release fields, date precision, and market scope.
- `relationships`: subject–predicate–object assertions with status, confidence, optional validity interval, and batch.
- `entity_evidence`, `relationship_evidence`: claim-level links to sources with role, locator, and concise evidence note.
- `review_events`: append-only canonical promotion rationale. Agents do not create canonical approvals.

Status values distinguish `candidate`, `verified`, `review_required`, `canonical`, `retired`, and `example`. Confidence is separate: `unknown`, `low`, `medium`, or `high`.

## Research staging

| Migration | Tables and purpose |
|---|---|
| `003` | `research_import_runs`, raw `intake_candidate_records`, and run/source links. |
| `004`–`005` | Verification assertions plus richer report fields and evidence references. Verification does not change entity status. |
| `006` | `normalization_proposals`; proposed names, categories, granularity, dates, rationale, and open questions. |
| `007` | `audit_findings` and links to candidates or proposed keys. Findings do not create entities. |
| `008` | Exact source-register rows as supplied by each worker, even when resolved to an existing source. |
| `009` | Separate context runs, product-purpose claims, and comparable benchmark observations. |
| `010` | Append-only discrepancy review runs, levels, dispositions, and types. These do not promote canon. |

Imports are idempotent by their recorded identities/digests and retain raw wording alongside normalized proposals.

## Connected reference extension

Migration `011` adds:

- `connected_imports`: frozen packet/verifier hashes and distinct worker identities.
- `reference_entities`: display/context fields for the bounded connected example.
- `relationship_details`: stable relationship key, scope, source assessment, and verifier note.
- `reference_claims`: sourced facts, comparisons, or unresolved claims with limits and evidence role.
- `visual_regions`: a component-to-parent link and display coordinates for conceptual diagrams.

It also proposes `MEMBER_OF_FAMILY`, `CONFIGURATION_OF`, and `REVISION_OF`. All seeded types and predicates remain `proposed` until human approval.

## Relationship conventions

- Use a stable entity key and an existing predicate. Propose new vocabulary explicitly; do not invent it during import.
- Scope every compatibility, containment, configuration, or substitution assertion narrowly enough to state revision, host, firmware, region, or evidence limits when relevant.
- `CONTAINS` may describe a documented constituent specification only when the scope makes clear that it is not a uniquely inspected physical package.
- `CONFORMS_TO` expresses form/specification conformance; `COMMUNICATES_USING` expresses an interface or bus; `IMPLEMENTS` expresses a command protocol or standard.
- `STANDARDIZED_BY` identifies the responsible standards organization, not manufacture or ownership.
- Visual-region labels and positions do not create hardware facts. The linked relationship and its evidence carry the assertion.
- Canonical entities and relationships must have at least one `supports` evidence row; [SOURCE_POLICY.md](SOURCE_POLICY.md) adds the human decision requirements.
