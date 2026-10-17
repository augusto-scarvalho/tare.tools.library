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

    def run_materialize(self, ref: Path, *, language='pt-BR', extra=()):
        return subprocess.run([
            sys.executable,str(SCRIPT),'--reference',str(ref),'--source',str(self.source),'--root',str(self.root),
            '--document-id','research.test.materialized','--document-type','research','--status','RESEARCH',
            '--context','Workflow','--source-language',language,'--materialization-basis','FILE_LIBRARY_EXACT_EXPORT'
        ] + list(extra),text=True,capture_output=True)

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


    def snapshot(self):
        return {str(p.relative_to(self.tmp.name)): p.read_bytes() if p.is_file() else None
                for p in Path(self.tmp.name).rglob('*')}

    def denied_unchanged(self, ref, *, extra=(), diagnostic='DENY'):
        before = self.snapshot()
        result = self.run_materialize(ref, extra=extra)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(diagnostic, result.stdout)
        self.assertEqual(before, self.snapshot())

    def test_external_reference_has_no_effect(self):
        ref = self.write_ref()
        external = Path(self.tmp.name) / 'external.json'
        ref.rename(external)
        self.denied_unchanged(external)

    def test_invalid_arguments_and_reference_fields_have_no_effect(self):
        ref = self.write_ref()
        for option, value in [('--batch', '../escape'), ('--batch', 'C:escape'),
                              ('--batch', 'NUL'), ('--document-id', '../doc'),
                              ('--document-id', 'bad\\name')]:
            with self.subTest(option=option, value=value):
                self.denied_unchanged(ref, extra=[option, value])
        original = json.loads(ref.read_text())
        for key, value in [('file_library_id', '../escape'), ('reference_id', ''),
                           ('native_language', 3), ('title', None)]:
            with self.subTest(key=key):
                changed = dict(original, **{key: value})
                ref.write_text(json.dumps(changed))
                self.denied_unchanged(ref, extra=['--source-language', ''] if key == 'native_language' else ())
        ref.write_text(json.dumps(dict(original, suggested_contexts=[])))
        # CLI context takes precedence; explicitly empty context is invalid.
        self.denied_unchanged(ref, extra=['--context', ''])

    def test_replay_verifies_backing_bytes_and_does_not_duplicate(self):
        ref = self.write_ref()
        result = self.run_materialize(ref)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        before = self.snapshot()
        result = self.run_materialize(ref)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('ALREADY_CROSSWALKED', result.stdout)
        self.assertEqual(before, self.snapshot())
        cross = json.loads((self.root/'catalog/identity-crosswalk/file_abc123.json').read_text())
        (self.root/cross['source_path']).write_bytes(b'changed')
        self.denied_unchanged(ref, diagnostic='hash mismatch')

    def test_changed_input_after_copy_is_rejected(self):
        ref = self.write_ref()
        target = self.root/'catalog/corpus/original/file-library-materialized/file_abc123__study.md'
        target.parent.mkdir()
        target.write_bytes(self.source.read_bytes())
        self.source.write_bytes(b'new bytes')
        self.denied_unchanged(ref, diagnostic='target collision')

    def test_interruption_during_copy_replays_exact_bytes(self):
        from unittest.mock import patch
        from tools import materialize_library_reference as materializer
        ref = self.write_ref()
        target = self.root/'catalog/corpus/original/file-library-materialized/file_abc123__study.md'
        argv = [str(SCRIPT), '--reference', str(ref), '--source', str(self.source),
                '--root', str(self.root), '--document-id', 'research.test.materialized',
                '--document-type', 'research', '--status', 'RESEARCH',
                '--materialization-basis', 'FILE_LIBRARY_EXACT_EXPORT']

        def interrupt(src, dst):
            dst.write(src.read(1))
            raise RuntimeError('interrupted during copy')

        with patch.object(sys, 'argv', argv), patch.object(materializer.shutil, 'copyfileobj', interrupt):
            with self.assertRaisesRegex(RuntimeError, 'interrupted during copy'):
                materializer.main()
        self.assertFalse(target.exists())
        self.assertFalse(list(target.parent.glob('*.tmp')))
        result = self.run_materialize(ref)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(target.read_bytes(), self.source.read_bytes())

    def test_unrelated_historical_records_do_not_block(self):
        ref = self.write_ref()
        manifests = self.root/'catalog/corpus/manifests'
        for directory in (manifests, manifests/'translations/en'):
            (directory/'unrelated.json').write_text('{invalid', encoding='utf-8')
            (directory/'other.json').write_text(json.dumps({
                'document_id': '../unsafe', 'source_path': '../outside',
                'source_sha256': '0'*64,
                'provenance': {'source_path': '../outside', 'source_sha256': '0'*64}
            }), encoding='utf-8')
        result = self.run_materialize(ref)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.run_materialize(ref)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        english = self.write_ref(fid='file_english', language='en')
        result = self.run_materialize(english, language='en')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        cross = json.loads((self.root/'catalog/identity-crosswalk/file_english.json').read_text())
        self.assertEqual(cross['translation_state'], 'NOT_REQUIRED_NATIVE_ENGLISH')

    def test_used_unsafe_records_and_malformed_named_manifest_fail_before_effects(self):
        ref = self.write_ref()
        manifests = self.root/'catalog/corpus/manifests'
        named = manifests/'file_abc123__study.md.json'
        named.write_text('{invalid', encoding='utf-8')
        self.denied_unchanged(ref)
        named.unlink()
        used = manifests/'used.json'
        used.write_text(json.dumps({'document_id': 'safe', 'provenance': {
            'source_sha256': sha(self.source.read_bytes()), 'source_path': '../escape'
        }}), encoding='utf-8')
        self.denied_unchanged(ref)
        used.unlink()
        translated = manifests/'translations/en/used.json'
        translated.write_text(json.dumps({
            'source_sha256': sha(self.source.read_bytes()), 'source_path': '../escape'
        }), encoding='utf-8')
        self.denied_unchanged(ref)

    def test_partial_copy_and_manifest_replay(self):
        from unittest.mock import patch
        from tools import materialize_library_reference as materializer
        ref = self.write_ref()
        argv = [str(SCRIPT), '--reference', str(ref), '--source', str(self.source),
                '--root', str(self.root), '--document-id', 'research.test.materialized',
                '--document-type', 'research', '--status', 'RESEARCH',
                '--materialization-basis', 'FILE_LIBRARY_EXACT_EXPORT']
        original = materializer.atomic_json
        for stop in ('manifest', 'crosswalk'):
            with self.subTest(stop=stop):
                def interrupt(path, record):
                    if (stop == 'manifest' and 'manifests' in path.parts
                            or stop == 'crosswalk' and 'identity-crosswalk' in path.parts):
                        raise RuntimeError('injected interruption')
                    original(path, record)
                with patch.object(sys, 'argv', argv), patch.object(materializer, 'atomic_json', interrupt):
                    with self.assertRaisesRegex(RuntimeError, 'injected interruption'):
                        materializer.main()
        result = self.run_materialize(ref)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(list((self.root/'catalog/corpus/original').rglob('*.md'))), 1)
        self.assertEqual(len(list((self.root/'catalog/corpus/manifests').glob('*.json'))), 1)

    def test_record_collisions_and_escaping_paths_have_no_effect(self):
        ref = self.write_ref()
        manifest = self.root/'catalog/corpus/manifests/file_abc123__study.md.json'
        for value in [
            {'document_id': 'ok', 'provenance': {'source_path': '../escape', 'source_sha256': sha(self.source.read_bytes())}},
            {'document_id': 'ok', 'provenance': {'source_path': 'catalog/missing', 'source_sha256': '0'*64}},
            {'document_id': '../bad', 'provenance': {'source_path': 'catalog/missing'}},
        ]:
            with self.subTest(value=value):
                manifest.write_text(json.dumps(value))
                self.denied_unchanged(ref)
        manifest.unlink()
        cross = self.root/'catalog/identity-crosswalk/file_abc123.json'
        cross.write_text(json.dumps({'source_path': '../escape', 'reference_path': 'catalog/ref', 'document_id': 'ok'}))
        self.denied_unchanged(ref)

    def test_hash_deduplication_and_translation_state(self):
        first = self.write_ref()
        result = self.run_materialize(first)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        cross = json.loads((self.root/'catalog/identity-crosswalk/file_abc123.json').read_text())
        translation = self.root/'catalog/corpus/manifests/translations/en/test.json'
        translation.write_text(json.dumps({'source_path': cross['source_path'], 'source_sha256': cross['source_sha256']}))
        second = self.write_ref(fid='file_second')
        result = self.run_materialize(second)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        record = json.loads((self.root/'catalog/identity-crosswalk/file_second.json').read_text())
        self.assertEqual(record['materialization_status'], 'ALREADY_MATERIALIZED_BY_HASH')
        self.assertEqual(record['translation_state'], 'TRANSLATION_ALREADY_PRESENT')
        self.assertEqual(record['source_path'], cross['source_path'])
        self.assertEqual(len(list((self.root/'catalog/corpus/original').rglob('*.md'))), 1)

    def test_atomic_json_failure_preserves_previous_bytes(self):
        from unittest.mock import patch
        from tools import materialize_library_reference as materializer
        record = self.root/'catalog/identity-crosswalk/old.json'
        record.write_bytes(b'{"old": true}\n')
        before = self.snapshot()
        with patch.object(materializer.os, 'replace', side_effect=OSError('injected replace failure')):
            with self.assertRaisesRegex(OSError, 'injected replace failure'):
                materializer.atomic_json(record, {'new': True})
        self.assertEqual(before, self.snapshot())

    def test_named_manifest_identity_collision_has_no_effect(self):
        ref = self.write_ref()
        result = self.run_materialize(ref)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        cross = self.root/'catalog/identity-crosswalk/file_abc123.json'
        cross.unlink()
        manifest = self.root/'catalog/corpus/manifests/file_abc123__study.md.json'
        original = json.loads(manifest.read_text())
        for key, value in [('document_id', 'another.document'), ('reference_id', 'another.reference')]:
            changed = json.loads(json.dumps(original))
            if key == 'document_id':
                changed[key] = value
            else:
                changed['provenance'][key] = value
            manifest.write_text(json.dumps(changed))
            self.denied_unchanged(ref, diagnostic='manifest collision')

    def test_non_directory_output_ancestor_has_no_effect(self):
        ref = self.write_ref()
        obstruction = self.root/'catalog/corpus/original/file-library-materialized'
        obstruction.write_bytes(b'keep this file')
        self.denied_unchanged(ref, diagnostic='not a directory')


if __name__ == '__main__':
    unittest.main()
