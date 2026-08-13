from pathlib import Path
import unittest


ROOT=Path(__file__).resolve().parents[1]


class PagesWorkflowTests(unittest.TestCase):
    def test_candidate_owner_is_authority_gated_and_required_gate_runs_unit_suites(self):
        workflow=(ROOT/'.github/workflows/pages.yml').read_text(encoding='utf-8')
        gate=(ROOT/'.github/workflows/document-integrity.yml').read_text(encoding='utf-8')

        # The owner capability now exists, but production effects must remain
        # unreachable until the separately validated durable authority record exists.
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

        # This implementation packet installs capability only; it must not carry
        # the owner decision that activates it.
        self.assertFalse((ROOT/'site/PAGES_CUTOVER_AUTHORITY.json').exists())

        # Main branch protection continues to depend on a gate that executes both suites.
        self.assertIn('python -m unittest discover -s tests',gate)
        self.assertIn('python -m unittest discover -s tools/publisher/tests',gate)


if __name__=='__main__': unittest.main()
