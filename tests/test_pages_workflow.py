from pathlib import Path
import unittest


ROOT=Path(__file__).resolve().parents[1]


class PagesWorkflowTests(unittest.TestCase):
    def test_shadow_cannot_deploy_and_required_gate_runs_unit_suites(self):
        shadow=(ROOT/'.github/workflows/pages.yml').read_text(encoding='utf-8')
        gate=(ROOT/'.github/workflows/document-integrity.yml').read_text(encoding='utf-8')
        self.assertNotIn('actions/deploy-pages',shadow)
        self.assertNotIn('actions/upload-pages-artifact',shadow)
        self.assertNotIn('pages: write',shadow)
        self.assertNotIn('id-token: write',shadow)
        self.assertIn('group: github-pages',shadow)
        self.assertIn('python -m unittest discover -s tests',gate)
        self.assertIn('python -m unittest discover -s tools/publisher/tests',gate)


if __name__=='__main__': unittest.main()
