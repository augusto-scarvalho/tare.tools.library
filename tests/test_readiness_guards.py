from pathlib import Path
import json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from cutover_readiness_support import _find_metadata,workflow_ownership

class ReadinessGuardTests(unittest.TestCase):
    def test_published_materialization_wins_over_retained_incoming(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for rel in ('incoming/canary','research/canary'):
                packet=root/rel; packet.mkdir(parents=True)
                (packet/'document-metadata.json').write_text(json.dumps({'document_id':'research.pages.canary.v1'}),encoding='utf-8')
            (root/'research/canary'/'PUBLICATION_RECORD.json').write_text('{}',encoding='utf-8')
            self.assertEqual(_find_metadata(root,'research.pages.canary.v1').parent,root/'research/canary')

    def test_candidate_pages_write_with_incumbent_is_dual_owner_failure(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); workflows=root/'.github'/'workflows'; workflows.mkdir(parents=True)
            (workflows/'candidate.yml').write_text('permissions:\n  pages: write\n',encoding='utf-8')
            result=workflow_ownership(root,'legacy-owner')
            self.assertTrue(result['candidate_deploy_capable'])
            self.assertTrue(result['dual_owner'])
            self.assertEqual(result['active_owner_count'],2)
            self.assertEqual(result['state'],'DUAL_OWNER')
            self.assertEqual(result['status'],'FAIL')

    def test_candidate_only_is_valid_single_owner_state(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); workflows=root/'.github'/'workflows'; workflows.mkdir(parents=True)
            (workflows/'candidate.yml').write_text('permissions:\n  pages: write\n',encoding='utf-8')
            result=workflow_ownership(root,None)
            self.assertTrue(result['candidate_deploy_capable'])
            self.assertFalse(result['dual_owner'])
            self.assertTrue(result['single_owner_invariant'])
            self.assertEqual(result['active_owner_count'],1)
            self.assertEqual(result['state'],'CANDIDATE_ONLY')
            self.assertEqual(result['status'],'PASS')

    def test_no_owner_is_safe_but_explicit_transition_state(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'.github'/'workflows').mkdir(parents=True)
            result=workflow_ownership(root,None)
            self.assertFalse(result['dual_owner'])
            self.assertTrue(result['single_owner_invariant'])
            self.assertEqual(result['active_owner_count'],0)
            self.assertEqual(result['state'],'NO_OWNER')
            self.assertEqual(result['status'],'PASS')

if __name__=='__main__': unittest.main()
