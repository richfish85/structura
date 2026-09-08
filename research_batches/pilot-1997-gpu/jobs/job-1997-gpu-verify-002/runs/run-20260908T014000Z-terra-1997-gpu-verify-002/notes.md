# Independent verification notes — 1997 GPU

## Scope and method

Verified exactly the six keys frozen in `job-1997-gpu-scout-001`. No candidates were added, split, normalized, audited, or promoted. Each judgment uses only the source URL registered against that frozen candidate; wording distinguishes an announcement, a plan, a sale window, and an evidenced shipment.

## Coverage and boundaries

- Six frozen keys covered exactly once; no unknown keys.
- RIVA 128 and PERMEDIA 2 remain chip records. PowerWindow PWR128P, WHP-PS, and Xpert remain board records even where a chip is named.
- ViRGE/MX has evidence of sampling and planned production, but not a completed shipment event.
- Board sale/shipment references are bounded by the reported month/window and are not converted to exact dates.

## Evidence limits

The allowed register contains mostly single-source candidate evidence. NVIDIA's source is a retrospective corporate chronology; the PERMEDIA 2 source is an ELSA board-maker release; and the ATI report describes planned availability. These limits explain `review_required` outcomes and do not invalidate the recorded identities.

## Validation

`verification.csv` has the exact 19-column verification-report header, six data rows, unique candidate keys, and exactly the frozen scout-key coverage. Fields containing commas are CSV quoted. Result-manifest output hashes were recalculated after final serialization.
