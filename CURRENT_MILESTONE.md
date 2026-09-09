# Current milestone

Status: **complete**  
Milestone: **Agent control and repository reference layer**  
Owner decision: 2026-09-10

Future work must replace the fields in this file before implementation begins. Keep exactly one current milestone here; move useful history to `docs/decision-log.md` rather than accumulating active scopes.

## Scope

Create a concise agent-control and documentation layer that reflects the repository's current implementation. No product, schema, research-data, or application behavior changes.

## Acceptance criteria

- [x] Repository-wide agent rules define scope control, bounded delegation, one test pass, one final review, backlog routing, and stop conditions.
- [x] Root architecture, schema, source-policy, milestone, and backlog documents have distinct responsibilities.
- [x] The documents reflect migrations `001`–`011`, the manifest-driven snapshot build, read-only explorer, and non-canonical research workflow.
- [x] Relative Markdown references among the six root documents resolve.
- [x] One final bounded review is performed; non-blocking findings are recorded without starting another loop.

## Allowed files and areas

- `AGENTS.md`
- `ARCHITECTURE.md`
- `SCHEMA.md`
- `SOURCE_POLICY.md`
- `CURRENT_MILESTONE.md`
- `BACKLOG.md`

No other file may change in this milestone.

## Tests

After integration, run once:

1. A local Markdown-link check for the six allowed files.
2. `git diff --check`.
3. Confirm the diff contains only the six allowed files.

Do not run the application suite: this milestone changes documentation only, and the prior product checkpoint was tested before its separate commit.

## Delegation rules

Maximum one reviewer sub-agent. It receives only the six allowed documents plus the repository files needed to verify a specific factual claim. It may not edit files or recursively delegate.

## Stop conditions

Stop immediately when the acceptance criteria and defined checks pass. Put non-blocking review findings in [BACKLOG.md](BACKLOG.md). Fix only a broken reference, material factual error, security issue, data-corruption risk, or contradiction that prevents these acceptance criteria. Do not start a second review cycle or another milestone.

## Template for the next milestone

Replace the milestone name, status, scope, criteria, allowed files, tests, delegation limit, and stop conditions above. Acceptance criteria must be observable; allowed areas and exclusions must be explicit; tests must name exact commands or checks.
