# Verification Report 02 — 1998 CPU Launch Cohort

## What

This independent verification pass checked only the ten candidates in `01_scout_candidates.csv`. It did not discover additional candidates, normalize names, alter the database schema, import records, or promote anything canonical.

## Result

All ten candidates have sufficient primary-source support to remain in the bounded 1998 launch-cohort review queue. The records are not canonical approvals. Eight Intel/AMD source records are manufacturer-controlled primary evidence: three Intel press releases, one Intel chronology, three AMD filed press-release exhibits, and one AMD annual-report exhibit.

The key distinctions are preserved:

- Intel Pentium II 350/400 and 450, and Celeron 300A/333: introduction and same-day system/boxed availability are stated.
- Intel Celeron 266: introduction is exact on 1998-04-15, but PCs and boxed processors were only promised for the next few weeks; no exact commercial-availability date is claimed.
- Intel Pentium II Xeon 400: family introduction and component availability are exact on 1998-06-29, while boxed reseller availability is later in 1998; 512 KB and 1 MB cache options remain a granularity question.
- AMD-K6-2 family: AMD states an exact family introduction date of 1998-05-28 and shipment evidence, but does not establish launch speed-grade membership.
- AMD-K6-2 350: introduced and shipped during Q3 1998; exact day/month unavailable.
- AMD-K6-2 400: introduced and shipped in volume during Q4 1998; exact day/month unavailable and evidence is retrospective from January 1999.

## Inclusion recommendation

Retain all ten for human review as launch-cohort candidates. Their inclusion is based on a qualifying product/family introduction or shipment during 1998, not on a claim that every channel became available on the announcement date. The CSV records timing precision and availability gaps separately.

## Source limitations

The evidence is strong for manufacturer claims but not independent. Intel's chronology is also first-party, and the AMD annual report and filed exhibits repeat AMD's own statements. These sources do not establish regional sell-through, first retail appearance, ordering part numbers, package variants, or complete SKU enumeration. The AMD quarter statements provide interval evidence only; they must not be converted into exact dates. No secondary source was needed to resolve the ten candidate claims, and no source was treated as evidence for an unlisted candidate.

## Ontology and audit flags

1. Product introduction, component availability, boxed availability, first shipment, and volume shipment should remain typed events in later schema work.
2. The Pentium II Xeon 400 cache options may require variant/SKU-level treatment; this pass leaves that decision open.
3. The AMD-K6-2 family and its 350/400 MHz variants are intentionally separate candidate identities; a family date must not be inherited by a speed grade.
4. The Celeron 300A designation is preserved exactly; collapsing it to plain 300 would erase manufacturer wording and potentially merge identities.

## Stopping rationale

The pass stopped after each of the ten existing candidates had a primary-source claim, an evidence locator, a confidence/status assessment, and an explicit limitation or contradiction field. Further searching would likely add redundant manufacturer-controlled evidence rather than materially improve the cohort boundary. Independent market corroboration and SKU resolution belong to the later audit/human-review stages.
