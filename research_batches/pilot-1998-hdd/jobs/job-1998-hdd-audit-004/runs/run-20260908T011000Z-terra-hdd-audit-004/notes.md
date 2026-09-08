# HDD pilot audit notes

## Scope and method

This audit examined the four frozen scout keys and their independent verification hand-off. It did not create, alter, normalize, approve, or promote candidates. The proposed keys in `audit.csv` are omission leads only; they are not entities or candidate records.

The initial scout manifest explicitly bounded the sample to Quantum and IBM desktop/workstation fixed magnetic HDDs. The audit therefore checks that boundary as well as the candidate-level evidence.

## Findings

- The IBM Deskstar 25GP and 22GXP records are distinct variants, not duplicates.
- The Quantum EL and EX records should remain family-level. Their capacity ranges do not authorize newly split SKU records.
- IBM's limited 1998 OEM shipment and its Q1 1999 broad distributor/reseller availability are separate events. No later process may inherit the Q1 1999 timing as a 1998 retail launch.
- Quantum EL and EX both have production or announcement evidence, but exact first commercial-shipment evidence remains incomplete.
- Maxtor, Seagate, Western Digital, and IBM Microdrive are omission-search territory. The audit captures only source-backed proposed keys; it creates no candidates.

## Boundary cautions

Mass production, planned availability, a product debut, and first commercial shipment are different claims. The Seagate Cheetah and IBM Microdrive leads are retained specifically to prevent forecast or presentation language from becoming 1998 shipment evidence.

## Validation

- `audit.csv` has the exact 13-column `AUDIT_COLUMNS` header.
- 11 findings have unique IDs.
- Affected-key coverage is a subset of the four frozen scout keys.
- Proposed candidate keys occur only in omission leads and are not candidate rows.
- This run made no database or canonical writes.

## Recommended hand-off

Route the two Quantum timing gaps and IBM channel-timing guardrail to human review. If cohort expansion is authorized, dispatch separately frozen scout jobs for the omission leads, with product/segment boundaries declared before verification.
