from pathlib import Path
import json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tests')]
from cutover_readiness import generate
from readiness_fixture import make_readiness_fixture

class ReadinessFailureTests(unittest.TestCase):
    def test_missing_critical_path_blocks_safeguard(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); incumbent,output=make_readiness_fixture(root)
            p=root/'site'/'INCUMBENT_PROFILE.json'; data=json.loads(p.read_text())
            data['critical_paths'].append('missing.html'); p.write_text(json.dumps(data))
            receipt,errors=generate(root,output,incumbent,base_path='/tare.tools.research/',candidate_sha='candidate')
            self.assertFalse(receipt['rollback_drill']['rollback_ready'])
            self.assertTrue(errors)

if __name__=='__main__': unittest.main()
