import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class FrontierRegistryTests(unittest.TestCase):
    def records(self):
        return [json.loads(x) for x in (ROOT/'frontier/RESEARCH_POINTERS.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    def test_validator_passes(self):
        cp=subprocess.run([sys.executable,'tools/validate_research_frontier.py'],cwd=ROOT)
        self.assertEqual(cp.returncode,0)
    def test_registry_is_nonempty_and_unique(self):
        rs=self.records(); self.assertGreaterEqual(len(rs),100)
        self.assertEqual(len(rs),len({r['id'] for r in rs}))
        self.assertEqual(len(rs),len({r['normalized_title'] for r in rs}))
    def test_no_pointer_grants_architectural_authority(self):
        for r in self.records():
            self.assertEqual(r['authority'],'RESEARCH_ONLY_NO_IMPLEMENTATION_AUTHORITY')
            self.assertNotIn(r['status'],{'CURRENT','TARGET','IMPLEMENT'})
    def test_radar_is_projection_not_priority(self):
        for r in self.records():
            self.assertIn('NOT roadmap priority',r['radar_projection']['basis'])
            self.assertEqual(r['curation']['priority'],'UNTRIAGED')

if __name__=='__main__': unittest.main()
