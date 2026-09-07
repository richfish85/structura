# Scout Report 01 — 1998 CPU Launch Cohort

## What

The scout pass found ten useful candidates: seven Intel speed grades/variants, one AMD product family, and two AMD speed grades. All evidence comes from manufacturer-controlled primary records, including press releases, a manufacturer chronology, regulatory exhibits, and an annual report.

This is a test sample, not a complete census and not verified data.

## Why

The sample was chosen to break simple assumptions early. It includes immediate availability, delayed availability, quarter-only timing, retrospective confirmation, family-level launch language, cached and cacheless variants, multiple market segments, and one processor offered with different cache configurations.

## How the batch showed up

### One release date is insufficient

The sources distinguish at least:

- brand announcement
- product or family introduction
- processor announcement
- system availability
- component availability
- boxed/reseller availability
- first shipment
- volume shipment

For the Intel Pentium II 350/400 records, announcement and availability align on 1998-04-15. For the Celeron 266, the same announcement says systems and boxed products will arrive in the next few weeks. Storing `1998-04-15` as the Celeron release date would therefore overstate the evidence.

### Product family and speed grade are different identities

AMD gives an exact 1998-05-28 introduction date for the AMD-K6-2 family, but the primary records located in this pass do not enumerate the launch speed grades. Later records name 350 MHz and 400 MHz versions within quarters. The family date cannot be copied onto every speed grade without evidence.

### Frequency is not a sufficient model number

The press releases name speed grades but do not consistently provide ordering part numbers. The Celeron 300A also shows that suffixes matter: reducing it to `300 MHz` would merge a distinct manufacturer designation.

### Channel and configuration affect availability

The Pentium II Xeon 400 MHz announcement describes immediate component availability but later boxed reseller availability. It also names 512 KB and 1 MB L2 cache options at the same frequency. A future record may need to distinguish product variant from orderable SKU.

### Contemporary and retrospective sources serve different roles

AMD's January 1999 filing is useful evidence that 400 MHz processors were introduced and shipped during Q4 1998, but it cannot establish a specific 1998 day. Source publication date and claimed event interval must remain separate.

## Gaps exposed

- The current schema has one `announced_date` and one `release_date`; it cannot cleanly store multiple typed product events.
- `date_precision` lacks an explicit quarter value, although a range can represent it.
- Source tier does not capture whether corroborating records are genuinely independent; several AMD records repeat company statements through company filings.
- The pilot boundary does not yet say whether "1998 census" means launches in 1998 or every product commercially available during 1998.
- Cache, packaging, stepping, region, and ordering-part-number distinctions need a product/SKU rule before normalization.

## Stage decision

Do not import these candidates yet. Queue them for an independent verification pass after the census boundary and entity-granularity questions are answered.
