# Current milestone

Status: **complete**

Milestone: **Phone taxonomy and 1997–1998 pilot**

Owner decision: 2026-09-25

## Scope

Replace the top-level `Smartphones` product-form lane with `Phones`. Add the nested classes `Smartphones` and `Legacy Phones`, with the requested class-specific physical form-factor browse lanes. Use an era-aware smartphone classification: 1990s keyboard communicators may qualify through a documented operating environment and application functions; capacitive multi-touch is a modern attribute, not a historical requirement. Research a representative 1997–1998 launch cohort of at most six phone models, stage it in SQL as provisional candidates, and publish the resulting sourced dossiers and browse pages. This is not a market census. Do not build a general filtering engine, pathway, visual treatment, new schema or ontology vocabulary, or canonical promotion.

## Acceptance criteria

- [x] `Phones` replaces `Smartphones` beside Workstations, Servers, and Laptops.
- [x] Phone browse routes separate Smartphones and Legacy Phones and expose the specified physical subtypes as filters.
- [x] Research contains no more than six representative models across 1997–1998 and preserves introduction/availability uncertainty.
- [x] Candidate identity, class, cohort event, and form-factor claims have claim-specific evidence; smartphone-era interpretation and limits are explicit.
- [x] Verification and audit are independent from scouting and normalization; SQL remains provisional and no human decision is implied.
- [x] Generated links, searches, old category routes, and empty-lane explanations remain valid.
- [x] Repository unit suite, generated build, desktop browser check, narrow responsive breakpoint review, and one independent scope/provenance review completed; blocking findings were corrected during integration.

## Allowed files and areas

- `CURRENT_MILESTONE.md`, `README.md`, `ROADMAP.md`, `BACKLOG.md`
- `structura/explorer.py`, `structura/assets/reference.css`
- `tests/test_connected_explorer.py`
- `data/build-manifest.json`
- `research_batches/pilot-1997-1998-phones/**`

No other product features, schema migrations, existing research packet rewrites, visual module changes, or deployment configuration changes.

## Tests

Run the repository suite and generated build once after integration. Check generated links, search terms, cohort/class/form-factor pages, desktop rendering, and narrow layout rules. The embedded browser did not expose viewport emulation, so the narrow check reviewed the existing 600px and 480px breakpoints. Then conduct one independent scope and provenance review. Repeat a check only to resolve a milestone-blocking failure.

## Delegation rules

At most two non-recursive sub-agents: one verifier for the frozen scout candidates and one auditor for the coordinator normalization and merged packet. Give each only the relevant artifacts, fixed candidate set, evidence rules, and explicit stop condition. No open-ended scouting or expansion.

## Stop conditions

Mark complete when the phone taxonomy and bounded, independently reviewed candidate cohort are browseable and all acceptance criteria pass. Leave uncertain class labels or missing evidence provisional and list any non-blocking follow-up in `BACKLOG.md`. Do not start another audit/fix/audit loop.
