from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / 'tools' / 'materialize_library_reference.py'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class MaterializationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'research'
        (self.root / 'catalog/corpus' / 'library-references').mkdir(parents=True)
        (self.root / 'catalog/corpus' / 'manifests' / 'translations' / 'en').mkdir(parents=True)
        (self.root / 'catalog/corpus' / 'original').mkdir(parents=True)
        (self.root / 'catalog' / 'identity-crosswalk').mkdir(parents=True)
        self.source = Path(self.tmp.name) / 'source.md'
        self.source.write_bytes(b'# Exact source\nconteudo\n')

    def tearDown(self):
        self.tmp.cleanup()

    def write_ref(self, *, fid='file_abc123', reported=None, language='pt-BR') -> Path:
        ref={
            'schema_version':'1.0','reference_id':'lib.test','title':'study.md','file_library_id':fid,
            'native_language':language,'availability':'LIBRARY_REFERENCE_ONLY','materialized_bytes':False,
            'translation_status':'NOT_REQUIRED_NATIVE_ENGLISH' if language=='en' else 'BLOCKED_EXACT_SOURCE_NOT_MATERIALIZED',
            'priority':'P0','suggested_kind':'research','suggested_status':'RESEARCH','suggested_contexts':['Workflow'],
            'lineage_family':'test','lineage_order_hint':1,'reported_sha256':reported,
            'hash_status':'REPORTED_NOT_LOCALLY_VERIFIED' if reported else 'UNKNOWN','discovered_at':'2026-08-11T00:00:00Z','discovery_basis':'test','notes':''}
        p=self.root/'catalog/corpus'/'library-references'/f'{fid}.reference.json'
        p.write_text(json.dumps(ref),encoding='utf-8'); return p

    def run_materialize(self, ref: Path, *, language='pt-BR'):
        return subprocess.run([
            sys.executable,str(SCRIPT),'--reference',str(ref),'--source',str(self.source),'--root',str(self.root),
            '--document-id','research.test.materialized','--document-type','research','--status','RESEARCH',
            '--context','Workflow','--source-language',language,'--materialization-basis','FILE_LIBRARY_EXACT_EXPORT'
        ],text=True,capture_output=True)

    def test_reported_hash_mismatch_fails_without_effect(self):
        ref=self.write_ref(reported='0'*64)
        p=self.run_materialize(ref)
        self.assertEqual(p.returncode,3,p.stdout+p.stderr)
        self.assertFalse(any((self.root/'catalog'/'identity-crosswalk').glob('*.json')))
        self.assertFalse(any((self.root/'catalog/corpus'/'original').rglob('*.md')))

    def test_exact_materialization_creates_crosswalk_and_ready_translation(self):
        ref=self.write_ref(reported=sha(self.source.read_bytes()))
        p=self.run_materialize(ref)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        cross=json.loads((self.root/'catalog'/'identity-crosswalk'/'file_abc123.json').read_text())
        self.assertEqual(cross['reported_hash_verification'],'MATCH')
        self.assertEqual(cross['translation_state'],'READY_FOR_TRANSLATION')
        imported=self.root/cross['source_path']
        self.assertEqual(imported.read_bytes(),self.source.read_bytes())

    def test_native_english_materialization_does_not_request_translation(self):
        ref=self.write_ref(reported=sha(self.source.read_bytes()),language='en')
        p=self.run_materialize(ref,language='en')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        cross=json.loads((self.root/'catalog'/'identity-crosswalk'/'file_abc123.json').read_text())
        self.assertEqual(cross['translation_state'],'NOT_REQUIRED_NATIVE_ENGLISH')


if __name__ == '__main__':
    unittest.main()
