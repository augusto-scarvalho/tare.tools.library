from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PagesWorkflowTests(unittest.TestCase):
    def test_projection_workflow_has_no_deploy_or_publisher_capability(self):
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        gate = (ROOT / ".github/workflows/document-integrity.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("actions/upload-artifact@v4", workflow)
        self.assertIn("tools/build_pages.py", workflow)
        self.assertIn("tools/validate_pages_contract.py", workflow)
        self.assertIn("contents: read", workflow)
        self.assertNotIn("actions/upload-pages-artifact", workflow)
        self.assertNotIn("actions/deploy-pages", workflow)
        self.assertNotIn("pages: write", workflow)
        self.assertNotIn("id-token: write", workflow)
        self.assertNotIn("pages_cutover_authority", workflow)

        self.assertIn("python -m unittest discover -s tests", gate)
        self.assertNotIn("tools/publisher", gate)
        self.assertFalse((ROOT / "site/PAGES_CUTOVER_AUTHORITY.json").exists())
        self.assertFalse((ROOT / "site/PAGES_CUTOVER_AUTHORITY.proposed.json").exists())


if __name__ == "__main__":
    unittest.main()
