# Threat and Risk Notes

## Implementation risks

- SQLite permits a simple local start but will not serve concurrent public contributors well.
- Free-text locators and evidence notes may become inconsistent without later validation rules.
- Entity/predicate/object flexibility can hide weak modelling behind vague predicates.
- Schema migrations need backup and rollback procedures before valuable datasets accumulate.

## Data and research risks

- Prompt injection or malicious instructions can appear inside web pages, PDFs, repository files, and submitted records.
- Search-result repetition can make one unsupported claim look independently corroborated.
- Product announcement, shipment, retail availability, and review dates are not interchangeable.
- Manufacturer aliases and acquisitions can collapse historically distinct identities.
- Agent-generated normalization can erase uncertainty or merge separate products.
- Derived graphs and metrics can make weak evidence appear authoritative.

## Legal and ethical risks

- Bulk scraped specifications, images, manuals, and source excerpts may be copyright- or licence-restricted.
- Compatibility or repairability claims can cause cost, warranty, safety, or data-loss harm if presented without scope.
- Market-control and artificial-scarcity claims require stronger evidence than ordinary product facts.
- Contributor logs must avoid unnecessary personal information.

## Controls for the local foundation

- Store links, precise locators, and concise evidence notes rather than copied documents.
- Treat imports and research sources as untrusted.
- Preserve `supports`, `contradicts`, `context`, and `lead_only` evidence roles.
- Require supporting evidence before canonical promotion.
- Keep ontology terms proposed until tested and reviewed.
- Keep the explorer read-only and bound to localhost by default.
- Do not expose the local SQLite file through a public web server.

## Validation steps before expansion

- Threat-model any contributor or authentication feature before implementation.
- Define source licences and takedown procedures before publishing datasets.
- Add backups, migration tests, and immutable review history before bulk research.
- Test compatibility language with explicit device revision, firmware, region, and configuration scope.
- Audit any proposed openness or market metric for hidden normative assumptions.
