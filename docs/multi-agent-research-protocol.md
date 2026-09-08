# Multi-Agent Research Protocol v0.1

## What

This protocol makes Structura research repeatable across multiple Luna/Terra (or equivalent) agent runs without requiring an external queue, service, or shared database writer. It uses small JSON job/result manifests, stage CSVs, and SQLite as the canonical store.

The operating rule is simple:

```text
Coordinator -> bounded jobs -> isolated agent artifacts -> result manifests
             -> validate/hash -> non-canonical SQL staging -> HTML review
             -> independent next stage -> audit -> human review -> canonical promotion
```

Agents produce evidence-bearing work products. They do not promote records to canonical status.

## Why

Parallel research is useful only if ownership, scope, provenance, uncertainty, and handoff state remain inspectable. A manifest is the coordination record; an agent's CSV/JSON output is a proposed stage artifact. Only the coordinator writes SQLite: accepted artifacts may enter explicitly non-canonical staging before human review, while canonical promotion requires a recorded human decision.

This protocol is deliberately file-based so it can run locally today and move to a queue or worker service later without changing the stage contracts.

## How

### 1. Units and identifiers

Every run uses opaque, stable identifiers. Do not reuse an identifier after a job is cancelled or superseded.

- `batch_id`: stable research population, for example `pilot-1998-cpu-gpu-hdd`.
- `job_id`: one bounded assignment, for example `job-1998-cpu-scout-001`.
- `run_id`: one execution attempt of a job, for example `run-20260908T023000Z-luna-01`.
- `artifact_id`: one immutable output bundle, for example `artifact-job-...-run-...`.
- `record_key`: stable candidate/entity key from the input batch; never invent a replacement key during a retry.

Recommended format is lowercase ASCII with hyphens. Include a UTC timestamp plus a short worker label in `run_id`; do not put secrets, prompts, or long model names in identifiers.

The coordinator owns identifier allocation. Agents may propose record keys only in a scout result; the coordinator must reject collisions before scheduling downstream work.

### 2. Roles and bounded jobs

Each job has exactly one stage and one owner. A job may read earlier-stage artifacts but writes only to its own job directory.

| Stage | Purpose | Allowed output | Must not do |
|---|---|---|---|
| `scout` | Find in-scope candidates and leads within an explicit slice | Raw wording, event claims, sources, unknowns, conflicts | Verify, normalize, approve, or import |
| `verifier` | Independently check identity, category, timing, and scope | Field-level evidence, independent confirmations, conflicts | Expand population, erase uncertainty, or normalize away differences |
| `normalizer` | Map verified wording to approved ontology terms | Proposed normalized fields and unmapped-term flags | Approve ontology changes or canonical status |
| `auditor` | Test omissions, duplicates, weak evidence, scope/date/category errors | Findings and recommended follow-ups | Edit another agent's artifact or silently fix records |

Jobs must be bounded by at least one of: `record_keys`, manufacturer, category, geography, time interval, source set, or a declared search question. A job without a stopping rule is invalid.

For Luna/Terra allocation, prefer Luna for high-volume, bounded extraction and Terra for ambiguity-heavy verification, normalization review, or audit. This is a routing preference, not a truth score; the manifest records the actual model used.

### 3. File layout and ownership

Use one directory per batch and one directory per job:

```text
research_batches/<batch>/
  jobs/<job_id>/
    job_manifest.json       # coordinator-owned after dispatch
    runs/<run_id>/
      result_manifest.json  # agent writes once, then immutable
      output.csv             # stage-specific rows
      notes.md               # optional concise reasoning/limits
```

Ownership rules:

- Coordinator owns batch status, job manifests, result acceptance/rejection, merges, and the human-review queue.
- An agent owns only its current `runs/<run_id>/` directory until it submits a result.
- No agent edits another job's output, the active batch, `data/intake/`, or SQLite.
- The coordinator may copy accepted rows into a coordinator-owned merge area; preserve `artifact_id`, source paths, hashes, and original result files.
- SQLite has one writer: the coordinator. Parallel agents use read-only snapshots or CSV/JSON inputs. Coordinator imports before human review must remain in non-canonical staging or candidate status.

### 4. Dispatch and handoff states

Valid job states are:

`planned -> dispatched -> running -> submitted -> accepted`

Terminal alternatives are `rejected`, `blocked`, `cancelled`, and `superseded`. A result can be accepted as an artifact without being accepted as fact; acceptance means it passed the structural gate for the next stage.

Every handoff records:

- source job/run/artifact IDs;
- destination job ID and required input artifact IDs;
- coordinator decision and timestamp;
- unresolved conflicts and unknowns;
- whether the handoff is complete, blocked, or requires human input.

The destination agent may not start until required artifacts are present and their SHA-256 hashes match the manifest. If a source artifact changes, create a new artifact and downstream run; never overwrite in place.

### 5. Parallelism without collisions

The coordinator creates disjoint scopes before dispatch. Two active jobs must not claim the same `(batch_id, record_key, stage)` unless one is explicitly a second independent verification job with a distinct `independence_group` and source policy.

Safe parallel patterns:

- split scout by category/manufacturer;
- split verification by candidate slices;
- split normalization by category after verification;
- run an auditor over the complete frozen snapshot while another auditor checks a disjoint issue class.

Unsafe pattern: two workers writing one CSV, one SQLite file, or one mutable “master” JSON. Merge only after jobs submit immutable artifacts.

### 6. Independence and same-agent separation

The same agent identity (`agent_id`) must not scout and verify the same record, nor normalize and audit the same record, within one batch unless the coordinator explicitly marks the later work as a non-approval draft. A model family alone is not sufficient to establish independence; record `agent_id`, `model`, `run_id`, tools, source policy, and input artifact IDs.

At minimum, verification must differ from scouting by `agent_id` or by a declared independent run with a materially different source plan and no access to the scout's conclusions beyond the raw candidate key and scope. The coordinator must flag violations rather than silently accept them.

### 7. Source and uncertainty policy

Manifests record source-policy metadata: allowed source tiers, required primary-source preference, whether retrospective sources are allowed, whether web/archive access was used, and the access date. Results retain URL, publisher/origin, publication date, locator, evidence role, and concise notes per the existing workflow.

Agents must preserve `unknown`, `not found`, `conflict`, and `not applicable` distinctly. Never convert a missing date into an exact date; never turn a company repeat into independent corroboration; never copy a family event onto a speed grade without evidence. A blocked or incomplete job is a valid result.

When two runs describe the same source differently, the coordinator resolves identity by stable source key or exact URL and preserves each worker's raw title, type, dates, and scope note as a run-level source observation. A reused key pointing to a different URL, or a conflicting tier for the same resolved source, is rejected for human resolution rather than silently merged.

### 8. Idempotence, retry, and recovery

Retries create a new `run_id` but retain the same `job_id` and input snapshot hash. A retry must state the reason (`timeout`, `tool_failure`, `source_unavailable`, `quality_gate`, or `coordinator_request`) and what changed. The coordinator deduplicates by `(job_id, input_snapshot_sha256, attempt_number)` and never merges two attempts automatically.

If a run is interrupted, leave it `running` only until the coordinator's timeout; then mark it `blocked` or schedule a retry. If a result is malformed, reject it without editing and issue a new run. If sources disappear, preserve the old artifact and record the new result as a conflict or availability change.

### 9. Result gates

Before handoff, the coordinator checks:

1. manifest IDs, status, hashes, and row counts are internally consistent;
2. output schema matches the declared stage and contains no duplicate `record_key` within the job;
3. every material claim has a source or an explicit unknown/lead-only status;
4. scope and stopping rule are reported;
5. conflicts and omissions are listed, not hidden;
6. no same-agent approval violation exists;
7. no canonical SQLite write occurred.

Rejected artifacts remain available for audit. A failed quality gate is not permission to patch the worker's file in place.

### 10. Human canonical promotion

Only a human reviewer, or a coordinator acting on a recorded human decision, may promote an entity, relationship, source, or ontology term to canonical. The review record must name the object, prior state, new state, evidence artifacts, rationale, reviewer, and date. Automated agents can recommend `verified`, `review_required`, or `reject`; they cannot create a canonical `review_event` on their own.

Before approval, the coordinator may ingest structurally accepted artifacts into non-canonical staging so they can be inspected through HTML. After approval, the coordinator performs a separate canonical-promotion transaction, runs foreign-key/integrity checks, and regenerates the plain HTML explorer from SQL. HTML is read-only and never a source of truth.

### 11. Coordinator checklist

- [ ] Declare batch boundary, inclusion event, stopping rule, and source policy.
- [ ] Freeze the input snapshot and assign unique job IDs.
- [ ] Ensure active scopes are disjoint or explicitly independent.
- [ ] Dispatch stage-specific jobs with model/tool metadata requirements.
- [ ] Validate result manifests and CSVs before handoff.
- [ ] Preserve hashes, unknowns, conflicts, and failed attempts.
- [ ] Prevent same-agent self-approval.
- [ ] Queue material ambiguity for human review.
- [ ] Import structurally accepted artifacts only as non-canonical staging/candidates.
- [ ] Promote only human-approved records in a separate SQLite transaction.
- [ ] Run required tests and record the generated HTML export.

## Assumptions

- Local filesystem access is reliable enough for immutable artifact directories.
- CSV is adequate for row-oriented stage output; JSON manifests carry coordination metadata.
- SQLite remains a single-writer canonical store until concurrency needs justify a migration.
- Agents can report the model, tool versions, source policy, and input hashes they used.

## Risks left

- Filesystem coordination does not provide a distributed lock; the coordinator must be the only dispatcher and merger.
- Independence is procedural, not statistical: two agents may still repeat the same source error.
- Hashes prove artifact identity, not factual truth.
- A future service/queue will need an adapter, but should preserve these manifest fields and state transitions.
