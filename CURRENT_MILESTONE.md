# Current milestone

Status: **active**

Milestone: **Public GitHub Pages checkpoint**

Owner decision: 2026-09-10

## Scope

Make the Structura repository public and deploy the existing generated explorer through GitHub Pages at zero platform cost. Publish only validated static output. Keep the repository source-visible without granting an open-source or dataset licence, and do not begin contribution features.

## Acceptance criteria

- [ ] Public-repository review finds no credentials or private material.
- [ ] Repository visibility is public and its access/licensing boundary is documented.
- [ ] One GitHub Actions workflow runs tests, builds Structura, selects the successful snapshot, and uploads only its generated `site/` files.
- [ ] GitHub Pages uses the Actions workflow and reports a successful deployment.
- [ ] The live project URL loads the home page, search assets, one historical dossier, and the connected SSD/component/evidence path.
- [ ] Repository and deployed artifact expose no generated SQLite database.
- [ ] Defined checks run once, followed by one bounded final review.

## Allowed files and areas

- `CURRENT_MILESTONE.md`
- `README.md`
- `BACKLOG.md`
- `NOTICE.md`
- `.github/workflows/pages.yml`
- GitHub repository visibility, Pages configuration, and the resulting deployment

No application, schema, research packet, test, or generated reference file may be changed.

## Tests

After integration, run once:

1. `python -m unittest discover -s tests -v`
2. `python -m structura build`
3. Local inspection of the staged Pages artifact, including absence of database/research files.
4. Workflow syntax/action-reference check and `git diff --check`.
5. Live browser check after GitHub reports deployment success.

## Delegation rules

Maximum one read-only final reviewer. It receives only the workflow, publication documentation, milestone, and evidence from the defined checks. It may not edit files, recursively delegate, or initiate a second review.

## Stop conditions

Stop when every acceptance criterion is met. A credential, unintended private artifact, failed test/build, failed Pages deployment, broken live route, or exposed database is milestone-blocking. Put other findings in [BACKLOG.md](BACKLOG.md). Do not begin contribution tooling, product work, licensing selection, Vercel setup, or another audit/fix/audit loop.
