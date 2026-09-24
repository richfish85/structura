# Visual adoption plan

Status: **SSD benchmark refinement implemented; broader reuse and real-person validation pending** (2026-09-24)

## Owner-supplied SSD benchmark

The owner's `samsung_970_evo_500gb_exploded_3d.html` is a visual and interaction reference for this one product: a recognizable M.2 silhouette, direct part selection, adjustable separation, constrained turning, and contextual explanation. Its externally loaded older Three.js script, chat prompt hook, exact-looking package arrangement, and unsourced operational claims are not part of Structura's source of truth. In particular, the current research packet explicitly leaves package count, part markings, board positions, and the DRAM's detailed role unresolved. The adapted model keeps the pinned local Three.js version and labels its geometry schematic.

The navigation benchmark is two steps: select a constituent on the SSD dossier to inspect its compact SQL-derived connection panel, then choose `Open full component page` when deeper claims are useful. Put `Connected from` at the top of that panel and near the top of a direct component visit. Keep the panel limited to connections present in the current snapshot; its relationship links lead to the existing scope and source pages. Standard links remain available when scripting or WebGL is unavailable.

## What to adopt

The exploded hardware reference provides the right visual language: a recognizable object, separated layers, restrained materials, generous space and one adjacent information card. The bubble-sort reference contributes active-object highlighting and a synchronized explanation. Its character performance, theatrical staging, timed sequence and game loop do not belong in the core explorer.

Structura's rule is: **animate the hardware and its relationships**. Components may separate, connections may illuminate and evidence may appear with a selection. A mascot or character should not perform the operation for the user.

## Place in the current flow

Keep the existing route and reading order:

```text
search or browse
  -> dossier title and status
  -> Inside visual and equivalent component list
  -> Overview
  -> Connections
  -> relationship page
  -> evidence source
```

The visual belongs inside the existing `Inside` section. It is an optional, progressively enhanced view of the same SQL-derived entities and relationships. It must not become a separate landing experience, hide the navigation, replace the connections list or require 3D interaction to reach evidence.

Use one visual stage, one focused information card and one clear next action. Selecting a component should show its name, relationship to the parent, evidence state and an `Open relationship and evidence` link. The existing semantic component list remains available for keyboard, screen-reader, narrow-screen and WebGL-failure use.

## Rendering responsibilities

- **Three.js** runs the browser scene, selection, highlighting, fixed inspection views and exploded transitions.
- **Procedural templates** are the default for repeated hardware forms such as boards, packages, memory, cards, ports and cables. Stable SQL entity and relationship keys bind scene objects to the record.
- **Blender or CAD-authored GLB** is selective. Use it only when a product's silhouette, connector shape or mechanism materially affects understanding and the asset has acceptable provenance, rights and delivery cost.
- **SQL remains authoritative.** JavaScript and model files interpret approved records; they do not add identities, containment, compatibility or evidence.

The first implementation uses local, pinned assets so the static GitHub Pages build and current content-security boundary remain predictable.

## Fidelity states

Every visual must declare one of these states:

| State | What it may communicate | Required label |
|---|---|---|
| Conceptual | Documented identities and relationships using generic geometry | Conceptual; not to scale or position-accurate |
| Documented form | Evidence-backed dimensions, interfaces or orientation | Sources and model/revision scope |
| Observed assembly | Revision-matched package shape or placement | Specimen/source identity and image or model provenance |

The current Samsung 970 EVO data supports a **conceptual** constituent view. It does not support exact package count or board position. A convincing render must not silently imply otherwise.

## Interaction limits

- Start in a stable isometric overview; offer `Explode` and `Reset view`.
- Keep rotation and zoom constrained enough that users do not become lost.
- Select parts by pointer or from the equivalent text list; use the same visible focus state.
- Pause motion for selection, respect reduced-motion preferences and never require animation to understand a claim.
- Retain Structura's light editorial palette. Use colour to show the selected part, relationship or uncertainty rather than to decorate the scene.
- Do not add scores, avatars, timed tasks, collectibles or correctness celebrations to the evidence explorer.

## First implementation slice

The Samsung 970 EVO 500 GB dossier now has one opt-in visual enhancement:

1. Render a simplified M.2 board and generic controller, NAND and cache shapes from reusable procedural templates.
2. Mark the scene as conceptual and keep package positions deliberately schematic.
3. Support assembled, exploded and reset states without free-roaming navigation.
4. Bind each selectable part to its existing entity and `contains` relationship.
5. Show the selected relationship assessment and its existing evidence link beside the scene.
6. Preserve the current component cards as the complete fallback and leave all other pages unchanged.

This is a renderer and interaction proof, not a claim of a scalable asset catalogue. The initial geometry is generic and sourced relationships remain available in plain HTML.

## Validation gate

The implementation milestone should pass the existing build and link suite plus one browser check covering desktop, narrow screen, keyboard-only use, reduced motion, disabled JavaScript and simulated WebGL failure. The current page must remain usable in every fallback state. A user should be able to select one constituent, state that the view is conceptual and open the supporting relationship evidence without losing their place.

The deferred real-person trial should then compare the enhanced page with the preserved baseline. Its purpose is to decide whether the visual improves comprehension before the pattern expands to PC and phone pathways.

The first slice passed 42 repository tests, the generated build and local link checks. A browser pass covered desktop and 390 px layouts, keyboard selection, and simulated reduced motion, blocked JavaScript and unavailable WebGL 2. These checks establish implementation behaviour, not participant comprehension. Real-person validation remains pending.

## Reuse in the locked pathways

- **PC lifecycle:** show only the component, requirement and limiting relationship needed for the current question; use exploded placement when it explains replacement or installation.
- **Phone charging:** show the phone, port, cable and charger as one capability path; animate connection or negotiated capability, not electrical spectacle.

Both use the same selection card, evidence link, fidelity label and `unknown` treatment. The visual explains the evaluator's result; it does not calculate or override it.
