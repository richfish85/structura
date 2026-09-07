# Multi-agent batch templates

These templates are intentionally small and contain no historical facts. Copy them into a batch job directory and replace the placeholder values before dispatch.

## Files

- `job_manifest.template.json` — coordinator-owned assignment and input contract.
- `result_manifest.template.json` — agent-owned execution receipt and output contract.

Agents write stage rows to `output.csv` using the existing stage-specific intake schemas in `data/intake/` (or a coordinator-approved schema named in the job manifest). They do not write SQLite.

## Minimal use

1. Copy the job template to `research_batches/<batch>/jobs/<job_id>/job_manifest.json`.
2. Fill the bounded scope, input artifact hashes, stage, source policy, and worker metadata requirements.
3. Create `runs/<run_id>/` and copy the result template there.
4. The agent writes `output.csv`, fills the result manifest, and stops at `submitted`.
5. The coordinator validates, hashes, and records the handoff. Never overwrite a submitted run.

All timestamps are UTC ISO 8601. Empty arrays mean “none recorded”; `null` means “unknown or not applicable.”
