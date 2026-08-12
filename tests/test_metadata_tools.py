from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class MetadataToolTests(unittest.TestCase):
    def test_source_index_is_nonempty_and_tracking_params_removed(self):
        subprocess.run([sys.executable,'tools/build_source_index.py'],cwd=ROOT,check=True,capture_output=True,text=True)
        d=json.loads((ROOT/'sources'/'SOURCE_INDEX.json').read_text(encoding='utf-8'))
        self.assertEqual(d['documents_scanned'],sum(d['origin_counts'].values()))
        self.assertGreaterEqual(d['origin_counts']['chat-corpus-original'],13)
        self.assertEqual(d['origin_counts']['private-github-snapshot-2026-08-05'],93)
        self.assertGreater(d['unique_urls'],0)
        self.assertTrue(all('utm_source=' not in x['url'] for x in d['sources']))
    def test_lineage_never_mints_supersedes_from_metadata(self):
        subprocess.run([sys.executable,'tools/build_lineage_reconciliation.py'],cwd=ROOT,check=True,capture_output=True,text=True)
        d=json.loads((ROOT/'catalog'/'LINEAGE_RECONCILIATION.json').read_text(encoding='utf-8'))
        raw=json.dumps(d)
        self.assertNotIn('supersedes',raw.lower())
        formal=[x for x in d['families'] if x['family']=='formal-research-program'][0]
        self.assertEqual(formal['status'],'METADATA_VERSION_SEQUENCE_CONFIRMED_CONTENT_SUPERSESSION_PENDING')
        self.assertGreaterEqual(len(formal['version_sequence']),2)
    def test_expected_identity_assertions_are_reported_not_locally_verified(self):
        subprocess.run([sys.executable,'tools/apply_identity_assertions.py'],cwd=ROOT,check=True,capture_output=True,text=True)
        q=json.loads((ROOT/'catalog'/'IDENTITY_ASSERTIONS.json').read_text(encoding='utf-8'))
        self.assertEqual(len(q['assertions']),6)
        refs={}
        for p in (ROOT/'corpus'/'library-references').rglob('*.reference.json'):
            d=json.loads(p.read_text(encoding='utf-8')); refs[d['file_library_id']]=d
        for a in q['assertions']:
            r=refs[a['target_file_library_id']]
            self.assertEqual(r['hash_status'],'REPORTED_NOT_LOCALLY_VERIFIED')
            self.assertEqual(r['reported_sha256'],a['reported_sha256'])
    def test_canonical_baseline_pinner_uses_real_git_head(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)/'repo'; repo.mkdir(); subprocess.run(['git','init','-q',str(repo)],check=True)
            (repo/'NORTH_STAR.md').write_text('target\n',encoding='utf-8')
            subprocess.run(['git','-C',str(repo),'add','NORTH_STAR.md'],check=True)
            subprocess.run(['git','-C',str(repo),'-c','user.name=t','-c','user.email=t@x.invalid','commit','-q','-m','seed'],check=True)
            out=Path(td)/'baseline.json'
            subprocess.run([sys.executable,str(ROOT/'tools'/'pin_canonical_baseline.py'),str(repo),'--out',str(out),'--path','NORTH_STAR.md'],check=True)
            d=json.loads(out.read_text())
            head=subprocess.run(['git','-C',str(repo),'rev-parse','HEAD'],text=True,capture_output=True,check=True).stdout.strip()
            self.assertEqual(d['head'],head); self.assertEqual(d['status'],'PINNED_FROM_REAL_GIT_REPOSITORY')
if __name__=='__main__': unittest.main()
