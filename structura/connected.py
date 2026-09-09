"""Import a bounded, independently assessed reference packet without promotion."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from .db import connect, PROJECT_ROOT
from .intake import KEY_PATTERN
from .web import safe_external_url


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

TYPE_MAP = {'controller_family':'component','memory_technology':'component','component_specification':'component','form_factor_standard':'standard','interface_configuration':'interface','interface_standard':'interface','protocol_revision':'protocol','standards_organization':'organization'}
PREDICATE_MAP = {'member_of_family':'MEMBER_OF_FAMILY','manufactured_by':'MANUFACTURED_BY','uses_controller':'CONTAINS','uses_nand':'CONTAINS','uses_dram_cache':'CONTAINS','has_form_factor':'CONFORMS_TO','has_interface':'COMMUNICATES_USING','implements_protocol':'IMPLEMENTS','variant_of':'CONFORMS_TO','configuration_of':'CONFIGURATION_OF','specified_by':'STANDARDIZED_BY','revision_of':'REVISION_OF'}


def comparison_statement(metrics):
    values={m['metric']:m for m in metrics}
    read=values['sequential_read_up_to_MB_s'];write=values['sequential_write_up_to_MB_s'];after=values['sequential_write_after_TurboWrite_region_MB_s']
    dram=values['dram_cache_source_label']
    return (f"Samsung specifies the 500 GB model with {dram['left']} and the 1 TB model with {dram['right']}. "
            f"Listed sequential reads are up to {read['left']:,} and {read['right']:,} MB/s respectively. "
            f"Sequential writes are up to {write['left']:,} versus {write['right']:,} MB/s with TurboWrite; "
            f"beyond the TurboWrite region, the listed rates are {after['left']:,} versus {after['right']:,} MB/s.")


def validate_packet(packet: dict, verification: dict, root: Path = PROJECT_ROOT):
    if packet.get('version') != 1 or packet.get('canonical_approval') is not False:
        raise ValueError('Connected packet must be version 1 and non-canonical')
    if verification.get('canonical_approval') is not False:
        raise ValueError('Verification may not approve canonical status')
    if not packet.get('scout_agent') or packet['scout_agent']==verification.get('agent_id'):
        raise ValueError('Scout and verifier must differ')
    if verification.get('independent_of_agent') != packet['scout_agent']:
        raise ValueError('Verification does not identify this scout')
    for item in packet['inputs']:
        path=(root/item['path']).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file() or sha(path)!=item['sha256']:
            raise ValueError('Connected provenance hash mismatch: '+item['path'])
    for item in verification['input_artifacts']:
        path=(root/item['path']).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file() or sha(path)!=item['sha256']:
            raise ValueError('Verification provenance hash mismatch: '+item['path'])
    scout_inputs=[i for i in verification['input_artifacts'] if i['path'].endswith('/candidates.json')]
    verified_inputs=[i for i in packet['inputs'] if i['path'].endswith('/verification.json')]
    if len(scout_inputs)!=1 or len(verified_inputs)!=1:
        raise ValueError('Exactly one frozen scout and verification are required')
    if json.loads((root/verified_inputs[0]['path']).read_text(encoding='utf-8')) != verification:
        raise ValueError('Verification differs from the frozen normalization input')
    scout=json.loads((root/scout_inputs[0]['path']).read_text(encoding='utf-8'))
    source_inputs=[i for i in verification['input_artifacts'] if i['path'].endswith('/sources.json')]
    if len(source_inputs)!=1:
        raise ValueError('Exactly one frozen source register is required')
    source_register=json.loads((root/source_inputs[0]['path']).read_text(encoding='utf-8'))
    source_register={s['source_id']:s for s in source_register+verification.get('additional_sources',[])}
    scout_entities={e['record_key']:e for e in scout['entities']}
    scout_edges={e['record_key']:e for e in scout['relationship_candidates']}
    def keys(rows,field):
        found=[r[field] for r in rows]
        if any(not KEY_PATTERN.fullmatch(k) for k in found) or len(found)!=len(set(found)):
            raise ValueError('Invalid or duplicate connected keys: '+field)
        return set(found)
    entities=keys(packet['entities'],'key');sources=keys(packet['sources'],'key')
    keys(packet['relationships'],'key');keys(packet['claims'],'key')
    verdicts={v['record_key']:v for v in verification['relationship_verdicts']}
    entity_verdicts={v['record_key']:v for v in verification['entity_verdicts']}
    for s in packet['sources']:
        if not safe_external_url(s['url']) or not s['access_date'] or not s['title']:
            raise ValueError('Connected source requires URL, title and access date')
        original=source_register.get(s['key'])
        if not original or any(s[k]!=original[k] for k in ('url','publisher','access_date')):
            raise ValueError('Source identity differs from the assessed source register')
    for e in packet['entities']:
        if e['key'] not in entity_verdicts or entity_verdicts[e['key']]['verdict'] not in ('supported','qualified'):
            raise ValueError('Entity lacks independent support: '+e['key'])
        if e['source'] not in sources or not e['locator'] or not e['description']:
            raise ValueError('Entity evidence is incomplete')
        original=scout_entities.get(e['key'])
        if not original or e['name']!=original['raw_label'] or e['type']!=TYPE_MAP.get(original['proposed_entity_type'],original['proposed_entity_type']):
            raise ValueError('Entity identity differs from the assessed scout record')
    for r in packet['relationships']:
        v=verdicts.get(r['key'])
        if not v or v['verdict'] not in ('supported','qualified') or r['assessment']!=v['verdict']:
            raise ValueError('Relationship lacks matching independent assessment: '+r['key'])
        if r['subject'] not in entities or r['object'] not in entities or r['subject']==r['object']:
            raise ValueError('Relationship has invalid endpoints')
        if r['source'] not in sources or r['source']!=v['source_id'] or not r['scope'] or not r['locator'] or not r['evidence']:
            raise ValueError('Relationship source, scope or locator is missing or differs from verification')
        original=scout_edges.get(r['key'])
        if not original or any(r[k]!=original[k] for k in ('subject','object')) or r['predicate']!=PREDICATE_MAP.get(original['proposed_predicate']):
            raise ValueError('Relationship endpoints or predicate differ from the assessed assertion')
    for cl in packet['claims']:
        if cl['entity'] not in entities or cl.get('related_entity') and cl['related_entity'] not in entities:
            raise ValueError('Claim endpoint missing')
        if cl['source'] not in sources or not cl['locator'] or not cl['limits']:
            raise ValueError('Claim evidence is incomplete')
        if cl['kind']=='unresolved' and (cl['status']!='unknown' or cl['evidence_role']!='context'):
            raise ValueError('Unknowns must remain unknown and cite contextual evidence')
        if cl['kind']=='comparison' and (cl['key']!=verification['comparison_verdict']['record_key'] or verification['comparison_verdict']['verdict']!='supported'):
            raise ValueError('Comparison lacks independent support')
        if cl['kind']=='comparison':
            if cl['statement']!=comparison_statement(verification['comparison_verdict']['metrics']) or cl['entity']!=scout['comparison']['left'] or cl.get('related_entity')!=scout['comparison']['right']:
                raise ValueError('Comparison differs from assessed values or endpoints')
        if cl['kind']=='unresolved':
            original=next((u for u in scout['unresolved_claims'] if u['record_key']==cl['key']),None)
            if not original or cl['key']!=verification['unresolved_claim_verdict']['record_key'] or cl['statement']!=original['question']:
                raise ValueError('Unresolved claim differs from assessed question')
        if cl['kind'] not in ('comparison','unresolved'):
            raise ValueError('New claim kinds require an independent assessment contract')
    for v in packet['visual_regions']:
        if v['entity'] not in entities or v['parent'] not in entities:
            raise ValueError('Diagram endpoint missing')
        if not any(r['subject']==v['parent'] and r['object']==v['entity'] and r['predicate']=='CONTAINS' for r in packet['relationships']):
            raise ValueError('Diagram region has no assessed constituent relationship')


def import_connected(db: Path, packet_path: Path, verification_path: Path, root: Path = PROJECT_ROOT):
    packet=json.loads(packet_path.read_text(encoding='utf-8'))
    verification=json.loads(verification_path.read_text(encoding='utf-8'))
    validate_packet(packet,verification,root)
    with connect(db) as c:
        prior=c.execute('SELECT * FROM connected_imports WHERE packet_key=?',(packet['key'],)).fetchone()
        if prior:
            if prior['packet_sha256']!=sha(packet_path) or prior['verification_sha256']!=sha(verification_path):
                raise ValueError('Connected packet identity already exists with different content')
            return
        c.execute('INSERT INTO connected_imports(packet_key,packet_sha256,verification_sha256,scout_agent,verifier_agent) VALUES(?,?,?,?,?)',(packet['key'],sha(packet_path),sha(verification_path),packet['scout_agent'],verification['agent_id']))
        run=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        sources={}
        for s in packet['sources']:
            known=c.execute('SELECT id,source_key,url FROM sources WHERE source_key=? OR url=?',(s['key'],s['url'])).fetchone()
            if known:
                if known['url']!=s['url']: raise ValueError('Source key collision')
                sources[s['key']]=known['id'];continue
            c.execute('INSERT INTO sources(source_key,title,publisher,source_type,source_tier,url,publication_date,accessed_date,notes) VALUES(?,?,?,?,?,?,?,?,?)',(s['key'],s['title'],s['publisher'],'primary_document',1,s['url'],s.get('publication_date'),s['access_date'],s['limits']))
            sources[s['key']]=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        entities={}
        for e in packet['entities']:
            if c.execute('SELECT 1 FROM entities WHERE entity_key=?',(e['key'],)).fetchone():raise ValueError('Entity key collision: '+e['key'])
            c.execute("INSERT INTO entities(entity_key,name,entity_type_code,description,record_status,confidence) VALUES(?,?,?,?,'candidate','medium')",(e['key'],e['name'],e['type'],e['description']))
            eid=c.execute('SELECT last_insert_rowid()').fetchone()[0];entities[e['key']]=eid
            c.execute('INSERT INTO reference_entities(entity_id,connected_import_id,short_description,category,manufacturer,context_year,context_year_basis,model_number,role_note) VALUES(?,?,?,?,?,?,?,?,?)',(eid,run,e['description'],e.get('category'),e.get('manufacturer'),e.get('context_year'),e.get('context_year_basis'),e.get('model_number'),e['role_note']))
            c.execute("INSERT INTO entity_evidence(entity_id,source_id,field_name,evidence_role,locator,evidence_note) VALUES(?,?,'identity','supports',?,?)",(eid,sources[e['source']],e['locator'],e['description']))
        for r in packet['relationships']:
            c.execute("INSERT INTO relationships(subject_id,predicate_code,object_id,assertion_status,confidence,notes) VALUES(?,?,?,'candidate','medium',?)",(entities[r['subject']],r['predicate'],entities[r['object']],r['scope']))
            rid=c.execute('SELECT last_insert_rowid()').fetchone()[0]
            c.execute('INSERT INTO relationship_details(relationship_id,relationship_key,connected_import_id,scope,assessment,verifier_note) VALUES(?,?,?,?,?,?)',(rid,r['key'],run,r['scope'],r['assessment'],r['verifier_note']))
            c.execute("INSERT INTO relationship_evidence(relationship_id,source_id,evidence_role,locator,evidence_note) VALUES(?,?,'supports',?,?)",(rid,sources[r['source']],r['locator'],r['evidence']))
        for cl in packet['claims']:
            c.execute('INSERT INTO reference_claims(claim_key,entity_id,related_entity_id,connected_import_id,kind,title,statement,status,limits,source_id,locator,evidence_role,verifier_note) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(cl['key'],entities[cl['entity']],entities.get(cl.get('related_entity')),run,cl['kind'],cl['title'],cl['statement'],cl['status'],cl['limits'],sources[cl['source']],cl['locator'],cl['evidence_role'],cl['verifier_note']))
        for v in packet['visual_regions']:
            c.execute('INSERT INTO visual_regions(entity_id,parent_entity_id,label,x,y,width,height) VALUES(?,?,?,?,?,?,?)',(entities[v['entity']],entities[v['parent']],v['label'],v['x'],v['y'],v['width'],v['height']))
