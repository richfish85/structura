# Current milestone

Status: **active**

Milestone: **SSD model benchmark and connected component preview**

Owner decision: 2026-09-24

## Scope

Use the owner's `samsung_970_evo_500gb_exploded_3d.html` as an interaction and visual benchmark for the Samsung 970 EVO 500 GB only. Improve its existing conceptual Three.js model with useful inspection and explosion controls, without importing unsupported physical or operational claims. On that dossier, a normal click on a constituent opens a same-page component panel; the panel shows its recorded incoming and outgoing connections, relationship evidence links, and a clear link to its full page. Keep ordinary links functional without JavaScript. Bring "Connected from" near the top of the standalone component page.

## Acceptance criteria

- [ ] The SSD visual adopts the reference's useful inspection and exploded-view cues while plainly marking unverified geometry.
- [ ] Every selectable part and connection is derived from existing SQL keys and evidence; no supplied HTML claim is promoted into data.
- [ ] A normal click on an SSD constituent link opens a readable same-page preview, with an explicit full-page action and all currently recorded incoming/outgoing connections.
- [ ] Modified-click, no-JavaScript, and WebGL-failure paths still reach the existing component pages; the panel closes by button, Escape, and backdrop and restores focus.
- [ ] Standalone connected component pages put incoming parent context near the top without duplicating it below.
- [ ] Desktop/mobile, keyboard, reduced-motion, and link behavior pass browser verification.
- [ ] Unit suite, generated build/link checks, one final scope/provenance/accessibility review, public Pages deployment, and live page verification pass.

## Allowed files and areas

- `CURRENT_MILESTONE.md`
- `BACKLOG.md`
- `README.md`
- `docs/visual-adoption-plan.md`
- `structura/explorer.py`
- `structura/assets/ssd-visual.js`
- `structura/assets/reference.css`
- `tests/test_connected_explorer.py`

No schema, research packet, historical dossier, or other product/pathway changes.

## Tests

After integration, run the repository unit suite and generated build once. Check generated links, JS syntax, desktop/mobile browser behavior, keyboard/focus, reduced motion, no-JavaScript/WebGL fallback, and one final review. Re-run affected checks only after a blocking correction. Verify public Pages and the live dossier after publishing.

## Delegation rules

No delegation. Keep this benchmark to one product.

## Stop conditions

Mark complete and stop when acceptance criteria pass. Defer real-person validation and broader component-panel rollout to a later milestone.
