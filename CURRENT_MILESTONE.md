# Current milestone

Status: **complete**

Milestone: **Reconcile README, MVPs and roadmap**

Owner decision: 2026-09-10

## Scope

Bring public and planning documentation up to the current product state. Distinguish completed foundations, the next visual/usability work, locked public pathways, and exploratory contribution, gamification and community ideas. Do not promote exploratory ideas into implementation commitments.

## Acceptance criteria

- [x] README states the definitive hardware-tracker goal and current public checkpoint.
- [x] Product brief and milestone documents identify completed and pending MVP work consistently.
- [x] One concise roadmap separates `complete`, `next`, `planned` and `exploratory` work.
- [x] Contribution, gamification and social/community ideas retain evidence, governance and privacy boundaries.
- [x] Backlog and decision history reflect the current open questions.
- [x] Links and status wording passed one documentation check and one final review.

## Allowed files and areas

- `CURRENT_MILESTONE.md`
- `README.md`
- `ROADMAP.md`
- `BACKLOG.md`
- `docs/product-brief.md`
- `docs/mini-demo-plan.md`
- `docs/first-connected-explorer.md`
- `docs/pathway-implementation-plan.md`
- `docs/decision-log.md`

No schema, application, research packet, test, generated-site or deployment changes are allowed.

## Tests

After integration, run once:

1. Verify relative Markdown links in changed documents.
2. Check milestone/status terms for contradiction.
3. Confirm exploratory work is not described as implemented or approved.
4. Run `git diff --check`.
5. Perform one final scope and consistency review.

## Delegation rules

No delegation. This is a bounded documentation milestone.

## Stop conditions

Stop when the acceptance criteria are met and mark this milestone complete. Do not implement visuals, pathways, submissions, scoring, accounts, moderation or community features.
