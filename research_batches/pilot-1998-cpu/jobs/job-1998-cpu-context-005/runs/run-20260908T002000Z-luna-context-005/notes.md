# CPU Context Research Notes

Coverage is complete for all 22 assigned candidate keys: each has either manufacturer-stated context or an explicit gap. The intent file keeps claim scope at `manufacturer_stated`; no independent interpretation was promoted to fact.

## Benchmark decision

`benchmarks.csv` now contains six defensible SPEC CPU95 rows for Celeron 300, 300A, and 333 on the same Intel MU440EX/64 MB/UnixWare/Intel compiler configuration. SPECint95 and SPECfp95 use separate comparison groups. The official SPEC indexes show 8.30/11.3/12.3 SPECint95 and 6.88/9.01/9.50 SPECfp95 for 300/300A/333 respectively. These are standards-body published, vendor-submitted results with Intel as sponsor; they are comparable within each metric/configuration group, not generic CPU-only scores.

## Gaps

- Intel Pentium 266 and mobile Pentium II 300 have identity/date evidence but no sufficiently explicit target-problem and engineering-response statement in the bounded source set.
- AMD 366/380 are described as speed-roadmap/customer-demand responses, but the filings do not give a unique problem statement or detailed engineering change for each speed grade.
- Product positioning is manufacturer-stated and may reflect marketing incentives; it is not treated as neutral proof of user outcomes.
- Cache/package/orderable-SKU boundaries remain unresolved for Xeon and other variants.

## Source limitations

All sources are tier-1 manufacturer-controlled records, including AMD regulatory exhibits. No database or shared file was changed. No candidates were added. Researcher identifier: `luna-context-005`.
