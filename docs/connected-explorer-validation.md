# Connected Explorer validation — 2026-09-09

Status: local implementation checks passed; real-person trial pending.

## Automated checks

- `python -m unittest discover -s tests -v`: **41 tests passed**, final run 33.060 seconds after the historical-intake label correction.
- `python -m structura build`: passed against the frozen current manifest.
- Disposable `init --db data/validation-connected.db` and `check --db data/validation-connected.db`: passed.
- `python -m structura check`: passed on the populated current snapshot.
- `git diff --check`: passed; only line-ending conversion notices were printed.

Snapshot checked: `1b38920f0490d88a-1576cf2a`. Generated 182 HTML pages. Its file hashes and status are stored with its SQL under `data/builds/1b38920f0490d88a-1576cf2a`. Generated snapshots are ignored local outputs, not committed source.

The suite covers unchanged historical behavior, all 54 candidates, the 1997 repaired fields, 70 entities, 22 relationships, zero canonical records, connected import idempotency, separate verifier identity, altered endpoints/predicates/names/source URLs/comparison/unknown/diagram rejection, rollback after failure, identical public files from repeated builds, internal links/fragments/assets, and read-only serving with database/path-traversal denial. This is not a penetration test or an independent proof that source claims are true.

## Browser checks performed by the agent

A real in-app browser visited the local server on port 8770.

- Home to SSD; component map to Phoenix; incoming contains relationship to its source, locator and scope.
- Search submission for Celeron 300A returned its dossier. The purpose, event evidence, comparable benchmark group and expandable source limitations were inspected.
- Live NVMe query, no-result query and empty-query all-entry fallback were checked.
- Year directory to 1997 (9 CPU, 6 GPU, 5 storage) and its CPU filter; manufacturer directory to the two Samsung models.
- Discrepancies and sitemap navigation were inspected. All other generated internal destinations were covered by the automated link check, not individually browsed.
- Native keyboard Enter opened a component, expanded evidence and activated the skip link; focus landed on main content.
- At 390 x 844, the year catalogue and stacked SSD component map were visually inspected. Document width was 375 within the 390 viewport; no horizontal page overflow was observed on those samples.
- At 1280 x 900, comparison/unknown evidence was visually inspected. Document width was 1265 within the 1280 viewport.

Browser review exposed a misleading stale intake note. The renderer now labels original intake sources explicitly and directs readers to later release verification; raw research notes remain unchanged. Temporary viewport overrides were reset after review.

## Independent research boundary

The scout and verifier artifacts remain frozen. The separate verifier assessed 17 relationships as supported and five as qualified. An independent audit identified assertion-binding and component-evidence issues; coordinator changes and regression tests address these. One final independent re-audit confirmed those corrections and recorded two non-blocking hardening findings for future normalized packets: source/qualification binding and diagram-label binding. The current packet was found correct on both points. Neither verification nor agent audit promotes records to canonical status.

## Remaining verification and risks

- No real participant session has taken place. Use `usability-trial.md`; do not count this browser walkthrough as user evidence.
- No full screen-reader, cross-browser, 200% zoom or touch-device study was performed. Narrow viewport testing is not actual phone testing.
- No public or production deployment was made. Localhost is not accessible to remote participants as a shared website.
- Existing historical ambiguities and owner decisions remain visible. Sixty audit findings have open/follow-up dispositions; these are not sixty confirmed product errors.
- Diagram package positions/counts remain unknown; the view is conceptual. Manufacturer specs are not independent measurements. Source licensing and canonical promotion policy remain open.
- Editorial scope and descriptions still require research review; hash/assertion validation prevents known structural substitutions but cannot make arbitrary prose true.
