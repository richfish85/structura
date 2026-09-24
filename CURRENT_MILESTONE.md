# Current milestone

Status: **active**

Milestone: **Connected SSD visual prototype**

Owner decision: 2026-09-24

## Scope

Add one Three.js visual to the Samsung 970 EVO 500 GB dossier. Use the owner's new references for a spacious technical illustration, separated layers, clear part labels, and concise record cards. Keep the current dossier, component links, relationships, and evidence flow usable without WebGL or JavaScript. Do not expand to another product or pathway.

## Acceptance criteria

- [ ] The SSD dossier offers an opt-in 3D view with assembled, exploded, and reset states.
- [ ] Controller, NAND, and cache selections use the existing SQL entity and relationship keys and open their existing evidence pages.
- [ ] The scene and labels state that geometry is conceptual and does not establish package counts or positions.
- [ ] The semantic component cards and dossier navigation work without 3D.
- [ ] The visual adapts to narrow screens, keyboard use, reduced motion, and WebGL failure.
- [ ] The dependency is pinned, local, licensed, and included in generated static snapshots.
- [ ] Existing tests, build checks, one browser validation pass, and one final independent review pass succeed.
- [ ] The public Pages build succeeds and the live SSD dossier is verified.

## Allowed files and areas

- `CURRENT_MILESTONE.md`
- `README.md`
- `ROADMAP.md`
- `BACKLOG.md`
- `docs/decision-log.md`
- `docs/product-brief.md`
- `docs/pathway-implementation-plan.md`
- `docs/visual-adoption-plan.md`
- `NOTICE.md`
- `structura/build.py`
- `structura/explorer.py`
- `structura/assets/`
- `tests/test_connected_explorer.py`

No schema, research packet, historical dossier, contribution, pathway, or deployment configuration changes are allowed.

## Tests

After integration, run once:

1. Run the existing unit suite and `python -m structura build` once after integration.
2. Check generated links and the local Three.js asset path.
3. Validate desktop and narrow-screen interaction, keyboard selection, reduced motion, disabled JavaScript, and simulated WebGL failure in one browser pass.
4. Verify relative documentation links and run `git diff --check`.
5. Perform one final scope, provenance, and accessibility review.
6. Verify the public Pages build and live dossier after the push.

## Delegation rules

No delegation. Keep the implementation bounded to one dossier.

## Stop conditions

Stop when the acceptance criteria are met and mark this milestone complete. Do not extend the visual to other devices or begin pathway screens, submissions, scoring, accounts, or community features.
