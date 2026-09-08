# 1998 CPU Pilot — Status

- Batch key: `pilot-1998-cpu-gpu-hdd`
- Subset: CPU scout pass 01
- Status: **22 candidates scouted, independently verified, normalized, context-researched, and post-expansion audited; flagged records retained with reviewed discrepancy levels**
- Access date: 2026-09-08

## What

This first bounded pass records ten CPU candidates from Intel and AMD primary sources. The approved population is the **1998 launch cohort**: products newly introduced or first commercially shipped during 1998. It is intentionally not a census of every CPU still sold during that year.

## Why

The pass tests whether the current intake format preserves product identity, family/model boundaries, release timing, availability channels, market scope, source provenance, and uncertainty before research scales.

## How

- Seven Intel candidates come from contemporary Intel press releases and Intel's processor chronology.
- Three AMD candidates come from AMD press releases filed with the SEC and AMD's annual report.
- Raw manufacturer wording is preserved.
- A separate agent independently verified the bounded ten-candidate set. All ten remain candidates for human review; none has been normalized or promoted to canonical status.
- The scout and verification artifacts can now be imported into a disposable SQL review database and rendered as plain static HTML.
- A separate normalizer proposed labels, family/variant structure, qualifying events, and supported date precision for all ten records.
- An independent audit confirmed no duplicate identities but found nine omission-lead findings representing twelve proposed product keys. These leads remain outside the cohort.
- Two disjoint Luna scout jobs completed all twelve approved-scope omission keys, followed by one independent Terra verification job over the frozen outputs.
- The twelve expanded keys now have normalization proposals, and a post-expansion audit covers all 22 CPU candidates.
- All 22 candidates have a sourced “Why it existed” record or explicit gap. Six same-platform SPEC CPU95 observations cover the Celeron 300/300A/333 comparison; no weaker cross-configuration results were retained.
- Nine expanded keys are retained for ordinary human review. The two OverDrive output-speed keys require merge/restructure review, and Xeon 450 separately requires a qualifying-event decision.

## Stage gates

- [x] Scout candidates recorded
- [x] Primary sources registered
- [x] Scout observations recorded
- [x] Draft research criteria produced
- [x] Independent verification
- [x] Normalization proposal against candidate terminology
- [x] Omission and duplicate audit
- [x] Mobile and upgrade segment boundary decision
- [x] Omission-lead scout jobs
- [x] Independent verification of omission leads
- [x] Normalization proposals for omission-derived candidates
- [x] Purpose and benchmark context research
- [x] Post-expansion audit across all 22 CPU candidates
- [x] Initial human review and discrepancy disposition
- [ ] Canonical import

## Current boundary

This sample is a **1998 launch cohort**, not a census of every CPU commercially present during 1998. Mobile and upgrade processors are explicitly in scope, with separate segment labels and counts. The expanded review database contains 22 non-canonical candidate rows. OverDrive 300/333 remain two frozen keys at `L3`; no merge or reinterpretation occurs without verified documentary or attributable involved-party evidence. Xeon 450 remains at `L3`: its specifications and design are useful, while announcement versus completed shipment remains an open cohort-boundary question.
