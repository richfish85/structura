# Product Brief

## What

Structura is an evidence-backed hardware tracker: a durable record of products, components, configurations, standards, capabilities, relationships and change over time. SQL holds the authoritative knowledge. Visuals confirm what the records describe, while public pathways turn selected parts of that knowledge into immediate answers.

## Why

Public hardware knowledge is fragmented across manufacturer documents, standards, contemporary reviews, teardowns, repair guides, archives, market records, and enthusiast databases. A shared schema can make the joins visible:

- device to component
- component to interface, protocol, power, control, and form factor
- product to manufacturer, designer, supplier, owner, and standards body
- one generation to the next
- evidence to each identity, date, and relationship

This may eventually support investigation of replaceability, standardisation, integration, supplier concentration, proprietary control, and alleged scarcity. Those are research questions, not preloaded conclusions.

Structura is not defined by either of its first public use cases. PC lifecycle readiness and phone accessory capability are practical lenses over the same tracked hardware record. They test whether the underlying knowledge is understandable and useful without reducing the project to a comparison or recommendation site.

### What definitive means

Definitive means identity-resolved, connected, time-aware and traceable—not instantly complete. Structura should preserve model and regional variants, constituent parts, standards, capabilities, lifecycle events, evidence conflicts and known gaps. Coverage can grow gradually; an unsupported certainty would weaken the record more than an explicit absence.

## How

### MVP 0 — product census

Start with the 1998 launch cohort for CPU, GPU, and HDD products: products newly introduced or first commercially shipped during 1998. Capture identity, manufacturer, category, model number, typed launch evidence, source quality, confidence, and conflicts. Do not claim coverage of older products that remained on sale during the year.

### Ontology exercise

Deeply model one ordinary object—an M.2 NVMe SSD or Ethernet NIC—across physical, mechanical, electrical, signal, protocol, command, logical, control, containment, compatibility, manufacturing, standardisation, and constraint relationships.

### Inspection interface

Use plain server-rendered HTML to test whether people can find entities, follow relationships, inspect evidence, and notice classification problems before selecting a visual identity.

### Product layers

1. **Tracked knowledge:** SQL records stable identities, relationships, claims, evidence, review state and time-bounded context.
2. **Visual confirmation:** derived views show a device, its parts and the relevant relationship path. A visual position or label never creates a hardware fact.
3. **Immediate use:** a person starts with a concrete task and receives a bounded result, explanation, evidence and visible unknowns.

The first two immediate-use pathways are fixed in [public-use-cases.md](public-use-cases.md). Their staged delivery plan is [pathway-implementation-plan.md](pathway-implementation-plan.md).

## Explicit non-goals for the local foundation

- complete hardware coverage
- purchasing recommendations or price tracking
- unsupported compatibility claims
- broad product rankings, affiliate-led comparisons or automatic purchase recommendations
- a scored Hardware Openness Index
- community accounts, moderation, or contribution workflows
- automatic promotion of agent research
- Neo4j or a second canonical data store
- polished branding or production deployment
