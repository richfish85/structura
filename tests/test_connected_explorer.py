from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from structura.build import build, current_snapshot, validate_manifest
from structura.connected import import_connected, validate_packet
from structura.db import PROJECT_ROOT, connect, validate
from structura.explorer import create_reference_app, validate_site


class ConnectedExplorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='structura-test-')
        cls.root = Path(cls.temp.name)
        for directory in ('research_batches','schema','structura'):
            shutil.copytree(PROJECT_ROOT/directory,cls.root/directory,ignore=shutil.ignore_patterns('__pycache__'))
        (cls.root/'data').mkdir()
        shutil.copy2(PROJECT_ROOT/'data/build-manifest.json',cls.root/'data/build-manifest.json')
        cls.result=build(cls.root)
        cls.snapshot=current_snapshot(cls.root)
        cls.db=cls.snapshot/'structura.db'
        cls.manifest=json.loads((cls.root/'data/build-manifest.json').read_text(encoding='utf-8'))
        cls.packet_path=cls.root/cls.manifest['connected']['packet']['path']
        cls.verification_path=cls.root/cls.manifest['connected']['verification']['path']
        cls.packet=json.loads(cls.packet_path.read_text(encoding='utf-8'))
        cls.verification=json.loads(cls.verification_path.read_text(encoding='utf-8'))

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def test_complete_current_dataset_is_noncanonical_connected_and_sourced(self):
        status=self.result['status']
        self.assertEqual(status['historical_candidates'],54)
        self.assertEqual(status['relationships'],22)
        self.assertEqual(status['canonical_entities'],0)
        self.assertEqual(status['audit_findings'],76)
        self.assertEqual(status['usability_trial'],'pending_real_participants')
        with connect(self.db,read_only=True) as c:
            self.assertEqual(validate(c),[])
            self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(c.execute("SELECT count(*) FROM relationships r WHERE NOT EXISTS(SELECT 1 FROM relationship_evidence e WHERE e.relationship_id=r.id AND e.locator<>'' AND e.evidence_role='supports')").fetchone()[0],0)
            self.assertEqual(c.execute("SELECT count(*) FROM audit_findings WHERE source_url NOT LIKE 'http%' AND source_evidence IS NOT NULL").fetchone()[0],0)
            repaired=c.execute("SELECT a.* FROM audit_findings a JOIN research_import_runs r ON r.id=a.import_run_id JOIN research_batches b ON b.id=r.research_batch_id WHERE a.finding_key='hdd-aud-002' AND b.batch_key='pilot-1997-hdd'").fetchone()
            self.assertEqual(repaired['source_url'],'https://pc.watch.impress.co.jp/docs/article/970616/hdd.htm')
            self.assertEqual(repaired['source_evidence'],'Report distinguishes samples, scheduled production, and OEM-only supply.')

    def test_connected_import_retry_does_not_duplicate_claims_or_edges(self):
        tempdb=self.root/'retry.db';shutil.copy2(self.db,tempdb)
        import_connected(tempdb,self.packet_path,self.verification_path,self.root)
        with connect(tempdb,read_only=True) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM relationships').fetchone()[0],22)
            self.assertEqual(c.execute('SELECT count(*) FROM reference_claims').fetchone()[0],2)

    def test_endpoint_predicate_name_source_and_claim_tampering_rejected(self):
        changes=[
            lambda p:p['relationships'][0].update(object='pci-sig'),
            lambda p:p['relationships'][0].update(predicate='COMPATIBLE_WITH'),
            lambda p:p['entities'][0].update(name='Samsung 970 EVO Plus'),
            lambda p:p['sources'][0].update(url='https://example.com/fake'),
            lambda p:p['claims'][0].update(statement='This SSD is twice as fast.'),
            lambda p:p['claims'][1].update(key='invented-unknown'),
            lambda p:p['visual_regions'][0].update(entity='pci-sig'),
            lambda p:p.update(scout_agent=self.verification['agent_id']),
        ]
        for change in changes:
            p=copy.deepcopy(self.packet);change(p)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_packet(p,self.verification,self.root)

    def test_failed_render_leaves_current_pointer_and_previous_site_unchanged(self):
        pointer=(self.root/'data/current.json').read_bytes()
        old_html=(self.snapshot/'site/index.html').read_bytes()
        with patch('structura.explorer.render_explorer',side_effect=ValueError('synthetic render failure')):
            with self.assertRaisesRegex(ValueError,'synthetic render failure'):build(self.root)
        self.assertEqual((self.root/'data/current.json').read_bytes(),pointer)
        self.assertEqual((self.snapshot/'site/index.html').read_bytes(),old_html)

    def test_input_hash_failure_prevents_build_publication(self):
        manifest=copy.deepcopy(self.manifest);manifest['steps'][0]['files']['candidates']['sha256']='0'*64
        p=self.root/'data/bad-manifest.json';p.write_text(json.dumps(manifest),encoding='utf-8')
        pointer=(self.root/'data/current.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'hash mismatch'):build(self.root,p)
        self.assertEqual((self.root/'data/current.json').read_bytes(),pointer)

    def test_repeat_build_has_identical_public_files_and_status(self):
        second=build(self.root);snapshot=self.root/second['snapshot']
        def files(root):return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
        self.assertEqual(second['status'],self.result['status'])
        self.assertEqual(files(snapshot/'site'),files(self.snapshot/'site'))

    def test_every_local_link_fragment_and_asset_resolves(self):
        self.assertEqual(validate_site(self.snapshot/'site'),[])
        controller=(self.snapshot/'site/entities/samsung-phoenix.html').read_text(encoding='utf-8')
        self.assertIn('Identity and description',controller)
        self.assertIn('Samsung-NVMe-SSD-970-EVO-Data-Sheet',controller)
        ssd=(self.snapshot/'site/entities/samsung-970-evo-500gb.html').read_text(encoding='utf-8')
        self.assertIn('class="diagram-node"',ssd)
        self.assertIn('970evo-500gb-package-layout',ssd)
        self.assertIn('600 versus 1,200 MB/s',ssd)

    def test_ssd_visual_is_optional_and_bound_to_existing_relationships(self):
        site=self.snapshot/'site'
        ssd=(site/'entities/samsung-970-evo-500gb.html').read_text(encoding='utf-8')
        self.assertIn('id="visual-open" hidden',ssd)
        self.assertIn('id="visual-experience" class="visual-experience" hidden',ssd)
        self.assertIn('type="module" src="../assets/ssd-visual.js"',ssd)
        self.assertIn('class="diagram-node"',ssd)
        self.assertIn('One block per constituent type · package count and placement unverified',ssd)
        for key,relation in (
            ('samsung-phoenix','970evo-rel-003'),
            ('samsung-vnand-3bit','970evo-rel-004'),
            ('samsung-lpddr4-512mb','970evo-rel-005'),
        ):
            self.assertIn(f'data-part-key="{key}"',ssd)
            self.assertIn(f'data-evidence-href="../relationships/{relation}.html"',ssd)
            self.assertTrue((site/f'relationships/{relation}.html').is_file())
        for asset in ('ssd-visual.js','vendor/three/three.module.js',
                      'vendor/three/three.core.js','vendor/three/LICENSE'):
            self.assertTrue((site/'assets'/asset).is_file(),asset)
        sibling=(site/'entities/samsung-970-evo-1tb.html').read_text(encoding='utf-8')
        self.assertNotIn('ssd-visual.js',sibling)

    def test_ssd_component_preview_keeps_links_and_lists_current_connections(self):
        site=self.snapshot/'site'
        ssd=(site/'entities/samsung-970-evo-500gb.html').read_text(encoding='utf-8')
        self.assertIn('id="component-preview-layer" class="component-preview-layer" hidden',ssd)
        self.assertIn('id="visual-explosion" type="range"',ssd)
        self.assertIn('id="visual-turn-left"',ssd)
        self.assertIn('id="visual-turn-right"',ssd)
        self.assertIn('Open component page →',ssd)
        for key in ('samsung-phoenix','samsung-vnand-3bit','samsung-lpddr4-512mb'):
            self.assertIn(f'href="{key}.html" data-component-preview-key="{key}"',ssd)
            start=ssd.index(f'<template id="component-preview-{key}">')
            end=ssd.index('</template>',start)
            preview=ssd[start:end]
            self.assertLess(preview.index('Connected from'),preview.index('Connects to'))
            self.assertIn(f'href="{key}.html">Open full component page',preview)
            with connect(self.db,read_only=True) as c:
                relations=c.execute('''SELECT d.relationship_key FROM relationships r
                    JOIN relationship_details d ON d.relationship_id=r.id
                    JOIN entities e ON e.id=r.object_id WHERE e.entity_key=?
                    UNION SELECT d.relationship_key FROM relationships r
                    JOIN relationship_details d ON d.relationship_id=r.id
                    JOIN entities e ON e.id=r.subject_id WHERE e.entity_key=?''',(key,key)).fetchall()
            for relation in relations:
                self.assertIn(f'../relationships/{relation[0]}.html',preview)
        component=(site/'entities/samsung-lpddr4-512mb.html').read_text(encoding='utf-8')
        self.assertEqual(component.count('class="connected-from"'),1)
        self.assertLess(component.index('class="connected-from"'),component.index('<section id="inside">'))
        self.assertIn('970evo-rel-005.html',component)

    def test_category_hub_exposes_product_forms_and_functional_roles(self):
        site=self.snapshot/'site'
        hub=(site/'categories.html').read_text(encoding='utf-8')
        for label, path in (
            ('Workstations','product-form/workstations.html'),('Servers','product-form/servers.html'),
            ('Laptops','product-form/laptops.html'),('Smartphones','product-form/smartphones.html'),
            ('Smart Devices','product-form/smart-devices.html'),('IoT Devices','product-form/iot-devices.html'),
            ('Game Consoles','product-form/game-consoles.html'),('Input','functional-role/input.html'),
            ('Processing','functional-role/processing.html'),('Storage','functional-role/storage.html'),
            ('Output','functional-role/output.html')):
            self.assertIn(label,hub)
            self.assertTrue((site/'categories'/path).is_file(),path)
        self.assertTrue((site/'categories/product-form.html').is_file())
        self.assertTrue((site/'categories/functional-role.html').is_file())
        workstations=(site/'categories/product-form/workstations.html').read_text(encoding='utf-8')
        self.assertIn('Intel Pentium II Xeon processor 400 MHz',workstations)
        empty=(site/'categories/product-form/smartphones.html').read_text(encoding='utf-8')
        self.assertIn('planned coverage lane',empty)
        processing=(site/'categories/functional-role/processing.html').read_text(encoding='utf-8')
        self.assertIn('Intel Pentium II Xeon processor 400 MHz',processing)
        self.assertIn('3Dlabs PERMEDIA 2 graphics processor',processing)

    def test_reference_server_is_read_only_and_cannot_expose_database(self):
        app=create_reference_app(self.snapshot/'site')
        dbhash=hashlib.sha256(self.db.read_bytes()).hexdigest()
        for path,method,expected in [('/','GET','200'),('/entities/samsung-phoenix.html','GET','200'),('/','POST','405'),('/../structura.db','GET','404'),('/%2e%2e/structura.db','GET','404'),('/does-not-exist','GET','404')]:
            headers=[]
            app({'PATH_INFO':path,'REQUEST_METHOD':method},lambda status,h:headers.append((status,h)))
            self.assertTrue(headers[0][0].startswith(expected),(path,headers))
        self.assertEqual(hashlib.sha256(self.db.read_bytes()).hexdigest(),dbhash)


if __name__=='__main__':unittest.main()
