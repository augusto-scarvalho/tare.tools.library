from __future__ import annotations
import json
from pathlib import Path
import subprocess,sys,tempfile,unittest
HERE=Path(__file__).resolve().parent; SRC=HERE.parent/'src'; sys.path.insert(0,str(SRC))
from tare_tools_publisher.github_cli_backend import GitHubCliBackendError, plan, publish

def git(repo,*args):
    p=subprocess.run(['git','-C',str(repo),*args],text=True,capture_output=True,check=True); return p.stdout.strip()
class GitHubCliBackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); root=Path(self.tmp.name); self.repo=root/'repo'; self.pd=root/'packet'; self.repo.mkdir(); self.pd.mkdir()
        subprocess.run(['git','init','-q',str(self.repo)],check=True); (self.repo/'README.md').write_text('seed\n')
        subprocess.run(['git','-C',str(self.repo),'add','README.md'],check=True)
        subprocess.run(['git','-C',str(self.repo),'-c','user.name=test','-c','user.email=test@example.invalid','commit','-q','-m','seed'],check=True)
        (self.pd/'study.md').write_text('# Study\n')
        m={'packet_version':'1.0','document_id':'research.workflow.github-plan-test','document_type':'research','status':'RESEARCH','repository':'tare.tools.research','bounded_contexts':['Workflow'],'artifacts':['study.md'],'canonical_change':False}
        self.packet=self.pd/'PUBLISH_MANIFEST.json'; self.packet.write_text(json.dumps(m))
    def tearDown(self): self.tmp.cleanup()
    def test_plan_is_network_free_and_creates_no_branch(self):
        before=git(self.repo,'show-ref')
        r=plan(self.packet,self.repo,'example/tare.tools.research')
        self.assertEqual(r.outcome,'PLANNED_REMOTE'); self.assertFalse(r.remote_effects); self.assertFalse(r.applied)
        self.assertEqual(git(self.repo,'show-ref'),before)
    def test_apply_requires_explicit_remote_authority(self):
        with self.assertRaisesRegex(GitHubCliBackendError,'REMOTE_EFFECTS_NOT_AUTHORIZED'):
            publish(self.packet,self.repo,'example/tare.tools.research',apply=True,allow_remote_effects=False)
        p=subprocess.run(['git','-C',str(self.repo),'branch','--list','docs/publish/*'],text=True,capture_output=True)
        self.assertEqual(p.stdout.strip(),'')
    def test_invalid_repository_slug_denied(self):
        with self.assertRaises(GitHubCliBackendError): plan(self.packet,self.repo,'bad-slug')
if __name__=='__main__': unittest.main()
