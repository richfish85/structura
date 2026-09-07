PRAGMA foreign_keys = ON;

INSERT OR IGNORE INTO entity_types(code, label, description, ontology_status) VALUES
('product', 'Product', 'A commercially identifiable hardware product or product configuration.', 'proposed'),
('product_family', 'Product family', 'A named family containing one or more product models or configurations.', 'proposed'),
('company', 'Company', 'A commercial manufacturer, designer, supplier, owner, or licensee.', 'proposed'),
('component', 'Component', 'A physical constituent of a device or other component.', 'proposed'),
('category', 'Category', 'A controlled classification term used for catalogue queries.', 'proposed'),
('interface', 'Interface', 'A defined physical, electrical, signal, or software boundary.', 'proposed'),
('protocol', 'Protocol', 'A communication or command protocol.', 'proposed'),
('standard', 'Standard', 'A published technical standard or specification.', 'proposed'),
('form_factor', 'Form factor', 'A mechanical size, shape, mounting, or keying definition.', 'proposed'),
('organization', 'Organization', 'A standards body, regulator, consortium, museum, or other institution.', 'proposed'),
('software', 'Software', 'An operating-system or application-level software entity.', 'proposed'),
('firmware', 'Firmware', 'Software embedded in or distributed for hardware control.', 'proposed');

INSERT OR IGNORE INTO predicates(code, label, relationship_family, description, ontology_status) VALUES
('INSTANCE_OF', 'instance of', 'classification', 'Classifies an entity under a controlled category or kind.', 'proposed'),
('MANUFACTURED_BY', 'manufactured by', 'manufacturing', 'Identifies the entity responsible for manufacturing the subject.', 'proposed'),
('DESIGNED_BY', 'designed by', 'ownership', 'Identifies the entity responsible for designing the subject.', 'proposed'),
('OWNED_BY', 'owned by', 'ownership', 'Identifies ownership of a company, specification, or technology.', 'proposed'),
('LICENSED_BY', 'licensed by', 'ownership', 'Identifies an entity licensing the subject or its use.', 'proposed'),
('CONTAINS', 'contains', 'containment', 'The subject physically or logically contains the object.', 'proposed'),
('OCCUPIES', 'occupies', 'physical', 'The subject physically occupies the object, such as a socket or bay.', 'proposed'),
('CONFORMS_TO', 'conforms to', 'mechanical', 'The subject conforms to a form factor, standard, or specification.', 'proposed'),
('RECEIVES_POWER_FROM', 'receives power from', 'power', 'The subject receives electrical power from the object.', 'proposed'),
('CONNECTS_VIA', 'connects via', 'signal', 'The subject has a physical, electrical, or signal connection via the object.', 'proposed'),
('COMMUNICATES_USING', 'communicates using', 'protocol', 'The subject communicates using the object protocol or bus.', 'proposed'),
('IMPLEMENTS', 'implements', 'command', 'The subject implements the object protocol, command set, or standard.', 'proposed'),
('EXPOSES', 'exposes', 'logical', 'The subject exposes the object as a logical resource or interface.', 'proposed'),
('CONTROLLED_BY', 'controlled by', 'control', 'The subject is controlled or configured by the object.', 'proposed'),
('REQUIRES', 'requires', 'dependency', 'The subject depends on the object or on a capability it provides.', 'proposed'),
('COMPATIBLE_WITH', 'compatible with', 'compatibility', 'Evidence supports compatibility within an explicitly stated scope.', 'proposed'),
('REPLACEABLE_WITH', 'replaceable with', 'replaceability', 'The subject can be replaced by the object within an explicitly stated scope.', 'proposed'),
('INTEGRATES', 'integrates', 'integration', 'The subject integrates a function or component represented by the object.', 'proposed'),
('RESTRICTED_BY', 'restricted by', 'constraint', 'The subject is constrained by the object, such as firmware or pairing requirements.', 'proposed'),
('STANDARDIZED_BY', 'standardized by', 'standardization', 'The subject standard or interface is maintained or standardized by the object.', 'proposed');

INSERT OR IGNORE INTO research_batches(batch_key, title, scope_note, workflow_status) VALUES
('pilot-1998-cpu-gpu-hdd', '1998 CPU, GPU, and HDD product census pilot', 'Test product identity, family/model boundaries, manufacturer normalization, and release-date evidence across three deliberately different categories. No compatibility or market-control conclusions in this batch.', 'planned');

INSERT OR IGNORE INTO schema_migrations(version) VALUES ('002_seed_ontology');
