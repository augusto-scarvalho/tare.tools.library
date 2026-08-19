"""Unit tests for tools in tare.tools.library (ingest, manifest builder, query)."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.ingest import ingest_document
from tools.build_manifest import build_library_manifest, save_manifest
from tools.query import get_adr, get_spec, search_library


class LibraryToolsTests(unittest.TestCase):
    def test_ingest_document_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_file = tmp_path / "sample_chat.md"
            source_file.write_text("# Sample Chat\nDiscussion on sandboxing.", encoding="utf-8")

            # Test successful ingestion
            res = ingest_document(
                source_path=source_file,
                doc_type="chat",
                title="Sample Chat Record",
                root_dir=tmp_path,
            )
            self.assertTrue(res.success)
            self.assertTrue(res.target_path.exists())
            self.assertEqual(res.target_path.parent.name, "chats")

            # Test duplicate rejection
            res_dup = ingest_document(
                source_path=source_file,
                doc_type="chat",
                title="Duplicate Attempt",
                root_dir=tmp_path,
            )
            self.assertFalse(res_dup.success)
            self.assertTrue(res_dup.is_duplicate)

    def test_build_manifest(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            adr_dir = tmp_path / "docs" / "adr"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-099_test.md").write_text("# ADR-099: Test ADR\n* AC-01: Must pass", encoding="utf-8")

            spec_dir = tmp_path / "specs"
            spec_dir.mkdir(parents=True, exist_ok=True)
            (spec_dir / "SPEC-TEST-001.md").write_text("# SPEC-TEST-001: Test Spec\n* AC-01: Must pass", encoding="utf-8")

            manifest = build_library_manifest(root_dir=tmp_path)
            self.assertEqual(manifest.total_documents, 2)
            self.assertEqual(len(manifest.adrs), 1)
            self.assertEqual(len(manifest.specs), 1)
            self.assertEqual(manifest.adrs[0].id, "ADR-099")
            self.assertEqual(manifest.specs[0].id, "SPEC-TEST-001")

            out_file = save_manifest(manifest, root_dir=tmp_path)
            self.assertTrue(out_file.exists())
            loaded = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(loaded["total_documents"], 2)

    def test_query_engine(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            adr_dir = tmp_path / "docs" / "adr"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-001_microkernel.md").write_text("# ADR-001: Microkernel Architecture\nDecoupled five planes.", encoding="utf-8")

            adr_text = get_adr("ADR-001", root_dir=tmp_path)
            self.assertIsNotNone(adr_text)
            self.assertIn("Microkernel Architecture", adr_text)

            results = search_library("Microkernel", root_dir=tmp_path)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].doc_id, "ADR-001_microkernel")


if __name__ == "__main__":
    unittest.main()
