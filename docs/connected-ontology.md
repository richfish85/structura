# Connected object ontology proposal — 2026-09-09

## What

The Samsung 970 EVO exercise uses existing proposed entity types and introduces three explicitly proposed predicates: MEMBER_OF_FAMILY, CONFIGURATION_OF and REVISION_OF. No term or record is promoted to canonical status.

## Why

A capacity model is not the whole family; PCIe generation/lane width is an interface configuration; NVMe 1.3 is a protocol revision. Treating every distinction as containment would misrepresent physical structure.

## How

- MEMBER_OF_FAMILY: product → product family.
- CONFIGURATION_OF: specified interface configuration → interface.
- REVISION_OF: protocol revision → protocol.
- CONFORMS_TO: device → mechanical form factor, or named form factor → its specification.
- CONTAINS: device → documented constituent specification. Phoenix/NAND/DRAM nodes here are shared descriptions of constituents, not uniquely identified packages from a physical specimen. The scope on each assertion must say this.
- COMMUNICATES_USING: device → PCIe interface configuration.
- IMPLEMENTS: device → NVMe revision.
- STANDARDIZED_BY: standard/protocol/interface → standards organization; not manufacture or corporate ownership.

Normalization maps scout-only type proposals onto existing component, protocol, interface, standard, form_factor and organization types. No controller-family or memory-technology types are silently added. Shared component specifications must not be interpreted as the exact same physical component across two products.

## Evidence and visual rules

Every displayed relationship has its own stable key, source, locator, scope, independent assessment and provisional status. A sourced unresolved question cites the boundary of the reviewed documentation; it is not a positive assertion of an unknown layout. The 2D view is a conceptual component diagram, not a teardown, scale drawing or pin map. Positions are presentation metadata stored separately from hardware facts.

Historical candidate rows keep their raw fields and normalization proposals. Year navigation indicates research cohort, not a silently resolved commercial release year. Company/category filters use proposed normalized labels and preserve the raw record in the dossier.
