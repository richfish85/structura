# Independent Verification Notes — Omission Lane 04

## Scope and independence

This run verified only the 12 frozen candidate keys in the coordinator manifest. It used the source URLs already present in the two frozen source registers and did not add candidates, normalize records, change a database, or promote any status. The verifier identity is `terra-verifier-omissions-04`, distinct from both Luna scout identities recorded in the input paths.

## Input integrity

All four frozen input artifacts matched the SHA-256 values declared in `job_manifest.json` before review.

## Findings

- AMD K6-2 366 and 380 are supported by AMD's retrospective Q4 filing as versions introduced and shipped in volume during the quarter ended 1998-12-27. They remain quarter-precision claims.
- AMD-K6/300 mobile is supported as an introduction during Q3 1998. The cited filing does not establish shipment or availability.
- Intel's Celeron 300 release supports exact introduction on June 8 and states boxed Celerons were then available to dealers/resellers. This is stronger than the scout's unknown boxed-channel note, but still does not identify a 300 MHz ordering part number.
- The Intel mobile 233/266 release supports exact same-day mobile-PC availability and manufacturer component-module availability for both speeds.
- Mobile Pentium II 300 and Pentium 266 depend on Intel's retrospective chronology for their exact introduction days; the allowed contemporary mobile source corroborates only that the 300 MHz product was recently introduced.
- Pentium II 333 has exact product introduction and system availability evidence. The later-quarter server/workstation configuration is not collapsed into that same availability event.
- The OverDrive source describes one processor, singularly, with 300 and 333 MHz output mappings for different Pentium Pro inputs and one MSRP. The two frozen output-speed keys therefore require a human merge/restructure decision, not separate-product approval.
- Pentium II Xeon 450 has a dated announcement and planned two-way system shipments later in October, but the source does not use an unambiguous introduction claim. Its cohort inclusion needs a human event-boundary decision.

## Limits

All cited evidence is first-party. No independent confirmation, part-number enumeration, regional sell-through evidence, or canonical decision is claimed.
