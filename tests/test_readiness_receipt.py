from pathlib import Path
import sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tests')]
from cutover_readiness import generate
from readiness_fixture import make_readiness_fixture

class ReadinessReceiptTests(unittest.TestCase):
    def test_green_shadow_remains_blocked_for_cutover(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); incumbent,output=make_readiness_fixture(root)
            receipt,errors=generate(root,output,incumbent,base_path='/tare.tools.research/',candidate_sha='candidate')
            self.assertEqual(errors,[])
            self.assertTrue(receipt['rollback_drill']['rollback_ready'])
            self.assertEqual(receipt['technical_readiness'],'BLOCKED')
            self.assertFalse(receipt['cutover_authorized'])

if __name__=='__main__': unittest.main()
