# Current milestone

Status: **complete**

Milestone: **Two-axis hardware category browse**

Owner decision: 2026-09-24

## Scope

Expand the public category experience with two browse axes: product form (`Workstations`, `Servers`, `Laptops`, `Smartphones`, `Smart Devices`, `IoT Devices`, `Game Consoles`) and functional role (`Input`, `Processing`, `Storage`, `Output`). Keep the existing SQL model and current CPU/GPU/Storage category pages. Derive the new browse tags from explicit source wording and existing normalized category values; show empty categories as planned coverage rather than inventing assignments. Do not add new entities, schema vocabulary, research claims, or visual work.

## Acceptance criteria

- [x] The category page presents both axes with clear explanations and links.
- [x] Every requested label has a stable browse page, including empty planned-coverage pages.
- [x] Product-form assignments use only explicit source wording; functional roles remain separate from product-form categories.
- [x] Existing category, manufacturer, year, search, connected explorer, and dossier routes remain available.
- [x] Empty pages explain that no current records are mapped rather than implying no such hardware exists.
- [x] Generated links and search terms include the new pages, and the layout works at desktop and narrow widths.
- [x] Unit suite, generated build, one browser check, and one final scope review pass.

## Allowed files and areas

- `CURRENT_MILESTONE.md`
- `BACKLOG.md`
- `README.md`
- `structura/explorer.py`
- `structura/assets/reference.css`
- `tests/test_connected_explorer.py`

No schema, research packet, historical dossier, visual module, or deployment configuration changes.

## Tests

Run the repository unit suite and generated build once after integration. Check generated links, category/search output, desktop/mobile category pages, and one final scope review. Re-run affected checks only after a milestone-blocking correction.

## Delegation rules

No delegation. Keep the taxonomy presentation bounded to the current snapshot.

## Stop conditions

Mark complete and stop when the requested labels are browseable and acceptance criteria pass. Defer new research coverage and canonical taxonomy promotion to a later milestone.
