from pathlib import Path
import hashlib,json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from pages_cutover_authority import AUTHORITY_PATH,CANDIDATE_OWNER,CRITICAL_BINDINGS,evaluate


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class PagesCutoverAuthorityTests(unittest.TestCase):
    def _fixture(self, root: Path, *, rollback_allowed=True):
        profile={
            'deploy_owner':None,
            'candidate_deploy_owner':CANDIDATE_OWNER,
            'ownership_state':'CANDIDATE_ONLY',
            'retired_deploy_owner':{'retired_branch_commit':'0'*40},
        }
        path=root/'site/INCUMBENT_PROFILE.json'; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(profile),encoding='utf-8')
        bindings={}
        for idx,(field,rel) in enumerate(CRITICAL_BINDINGS.items()):
            target=root/rel; target.parent.mkdir(parents=True,exist_ok=True)
            data=f'fixture-{idx}'.encode(); target.write_bytes(data); bindings[field]=sha(data)
        authority={
            'record_version':'1.0',
            'record_kind':'pages-cutover-owner-authority',
            'repository':'augusto-scarvalho/tare.tools.research',
            'decision_id':'pages.cutover.test.001',
            'decision':'authorize-cutover',
            'canary_id':'research.pages.canary.v1',
            'candidate_deploy_owner':CANDIDATE_OWNER,
            'qualified_owner_commit':'1'*40,
            'authorized_at':'2026-08-13T00:00:00Z',
            'owner':{'identity_ref':'github:augusto-scarvalho','role':'repository-owner'},
            'rollback_allowed':rollback_allowed,
            'bindings':bindings,
        }
        ap=root/AUTHORITY_PATH; ap.write_text(json.dumps(authority),encoding='utf-8')
        return authority

    def test_absent_authority_is_safe_inactive_state(self):
        with tempfile.TemporaryDirectory() as td:
            result,errors=evaluate(Path(td),'candidate')
            self.assertFalse(result['authorized']); self.assertEqual(result['reason'],'authority_absent'); self.assertEqual(errors,[])

    def test_valid_candidate_authority_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._fixture(root)
            result,errors=evaluate(root,'candidate')
            self.assertTrue(result['authorized']); self.assertEqual(errors,[])

    def test_bound_file_change_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._fixture(root)
            (root/'.github/workflows/pages.yml').write_text('changed',encoding='utf-8')
            result,errors=evaluate(root,'candidate')
            self.assertFalse(result['authorized']); self.assertTrue(any('owner_workflow_sha256' in e for e in errors))

    def test_rollback_requires_explicit_permission(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self._fixture(root,rollback_allowed=False)
            result,errors=evaluate(root,'rollback')
            self.assertFalse(result['authorized']); self.assertIn('rollback mode requires rollback_allowed=true',errors)

if __name__=='__main__': unittest.main()
