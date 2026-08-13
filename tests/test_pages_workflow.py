from pathlib import Path
import json
import subprocess
import sys
import unittest


ROOT=Path(__file__).resolve().parents[1]


class PagesWorkflowTests(unittest.TestCase):
    def test_candidate_owner_is_authority_gated_and_required_gate_runs_unit_suites(self):
        workflow=(ROOT/'.github/workflows/pages.yml').read_text(encoding='utf-8')
        gate=(ROOT/'.github/workflows/document-integrity.yml').read_text(encoding='utf-8')

        # The owner capability exists, but production effects remain reachable only
        # through the separately validated durable authority record on main.
        self.assertIn('actions/deploy-pages@v4',workflow)
        self.assertIn('actions/upload-pages-artifact@v4',workflow)
        self.assertIn('pages: write',workflow)
        self.assertIn('id-token: write',workflow)
        self.assertIn("if: github.event_name != 'pull_request' && github.ref == 'refs/heads/main'",workflow)
        self.assertIn('tools/pages_cutover_authority.py',workflow)
        self.assertGreaterEqual(workflow.count("if: needs.authorize.outputs.authorized == 'true'"),2)
        self.assertIn('needs: [qualify, authorize]',workflow)
        self.assertIn('needs: [authorize, package-pages]',workflow)
        self.assertIn('expected_materialized_inventory_digest',workflow)
        self.assertIn('group: github-pages',workflow)

        # Post-authorization invariant: an active authority record must exist and
        # independently pass the same fail-closed validator used by the workflow.
        authority=ROOT/'site/PAGES_CUTOVER_AUTHORITY.json'
        self.assertTrue(authority.is_file())
        for mode in ('candidate','rollback'):
            proc=subprocess.run(
                [sys.executable,str(ROOT/'tools/pages_cutover_authority.py'),'--root',str(ROOT),'--mode',mode],
                text=True,capture_output=True,check=False,
            )
            self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
            result=json.loads(proc.stdout)
            self.assertTrue(result['authorized'])
            self.assertEqual(result['reason'],'authorized')
            self.assertEqual(result['mode'],mode)
        self.assertTrue(json.loads(authority.read_text(encoding='utf-8'))['rollback_allowed'])

        # Main branch protection continues to depend on a gate that executes both suites.
        self.assertIn('python -m unittest discover -s tests',gate)
        self.assertIn('python -m unittest discover -s tools/publisher/tests',gate)


if __name__=='__main__': unittest.main()
