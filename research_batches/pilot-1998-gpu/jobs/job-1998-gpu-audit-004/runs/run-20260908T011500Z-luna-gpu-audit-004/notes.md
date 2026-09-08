# GPU Audit Notes — Frozen 1998 Scout After Independent Verification

## Scope and method

This audit covers exactly the eight frozen GPU keys and the independent verification report. It checks duplicate identity, chip/board/family boundaries, timing inheritance, category and cohort scope, evidence gaps, and omission leads. It does not edit the frozen scout or verifier files, normalize names, approve records, or write canonical/database state. Access date: 2026-09-08.

## Findings

- Intel740 and Intel Express 3D remain distinct chip and board identities. ATI RAGE 128GL and RAGE 128VR remain distinct variants; no duplicate merges are recommended.
- Banshee card timing is forecast-only. ATI GL/VR timing contains a September-versus-October planned-production conflict, and board timing must not be inherited by chip rows.
- Matrox MGA-G200 is announcement-only in the frozen evidence. NVIDIA rows have month-level chronology only. These are evidence/scope gaps, not approvals.
- Omission leads are recorded as proposed keys only: Savage3D; Voodoo2 and Canopus PURE3D II; RIVA TNT boards; MGA-G200 boards; ATI RAGE boards; ATI mobile Mobility-M/P; and professional/workstation leads including Revolution 3D, Permedia 3, and V2200.
- Mobile and professional leads remain separately labeled in the finding text and proposed keys. The Mobility report schedules volume production for Q1 1999, so it does not establish a qualifying 1998 shipment under the strict boundary.

## Constraints and unknowns

No candidate was added to the frozen set. Proposed keys are omission-search leads only. Board versus chip identity, regional/channel scope, first commercial shipment, exact date, and forecast-versus-shipment status remain unresolved where stated in audit.csv. New sources used for omission leads do not alter the registered frozen source set.

## Omission seed list

`s3-savage3d`; `3dfx-voodoo2`; `canopus-pure3d-ii`; `stb-velocity-4400`; `creative-graphics-blaster-riva-tnt`; `matrox-mga-g200-board`; `ati-rage-magnum`; `ati-rage-fury`; `ati-xpert-128`; `ati-rage-mobility-m`; `ati-rage-mobility-p`; `number-nine-revolution-3d`; `3dlabs-permedia-3`; `rendition-v2200`.

No canonical promotion or shared-file mutation occurred.

## Contract correction

The initial audit export used descriptive enum labels that were not part of the approved Structura contract. This isolated run was corrected without changing substantive evidence: `duplicate_check` became `duplicate`; `family_variant_boundary` and `chip_board_boundary` became `family_variant_overlap`; `timing_inheritance` became `date_inheritance`; `retain` became `resolved_no_change`; `review_required` and proposed follow-up findings became `follow_up`. The corrected CSV was revalidated against the exact approved enum sets.
