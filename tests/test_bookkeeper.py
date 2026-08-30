"""Unit tests for the Bookkeeper package in tare.tools.library."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.bookkeeper.dedup_detector import detect_duplicates, compute_similarity
from tools.bookkeeper.ssot_registry import (
    STATUS_CANONICAL,
    STATUS_NON_CANONICAL,
    STATUS_UNKNOWN,
    audit_ssot_registry,
    classify_status,
)
from tools.bookkeeper.tombstone_manager import apply_tombstone, verify_tombstones


class BookkeeperTests(unittest.TestCase):
    def test_similarity_computation(self):
        text1 = "This is a comprehensive architectural decision record for agentic computing."
        text2 = "This is a comprehensive architectural decision record for agentic systems."
        text3 = "Completely unrelated content about baking sourdough bread in a stone oven."

        sim_high = compute_similarity(text1, text2)
        sim_low = compute_similarity(text1, text3)

        self.assertGreater(sim_high, 0.60)
        self.assertEqual(sim_low, 0.0)

    def test_dedup_detector_temp_dir(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc_a = tmp_path / "doc_a.md"
            doc_b = tmp_path / "doc_b.md"
            doc_c = tmp_path / "doc_c.md"

            content_a = """---
title: System Architecture
---
The system microkernel provides five planes of execution including isolation, routing, and memory.
All agents must adhere to the immutable contract version 1 without prompt stuffing.
"""
            content_b = """---
title: System Architecture Duplicate
---
The system microkernel provides five planes of execution including isolation, routing, and memory.
All agents must adhere to the immutable contract version 1 without prompt stuffing.
"""
            content_c = """---
title: Database Schema
---
This document specifies the relational table layouts and indexing strategies for PostgreSQL instances.
"""

            doc_a.write_text(content_a, encoding="utf-8")
            doc_b.write_text(content_b, encoding="utf-8")
            doc_c.write_text(content_c, encoding="utf-8")

            report = detect_duplicates(tmp_path, similarity_threshold=0.80)
            self.assertEqual(len(report.duplicates_found), 1)
            self.assertTrue(report.has_exact_duplicates or report.has_near_duplicates)

    def test_ssot_registry_audit(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            doc1 = tmp_path / "ADR-001_initial.md"
            doc2 = tmp_path / "ADR-001_duplicate.md"

            doc1.write_text("---\ndoc_id: ADR-001\nstatus: CANONICAL_SSOT\n---\n# ADR-001: Initial", encoding="utf-8")
            doc2.write_text("---\ndoc_id: ADR-001\nstatus: CANONICAL_SSOT\n---\n# ADR-001: Conflict", encoding="utf-8")

            report = audit_ssot_registry(tmp_path)
            self.assertFalse(report.is_valid)
            self.assertEqual(len(report.violations), 1)
            self.assertEqual(report.violations[0].doc_id, "ADR-001")

    def test_status_vocabulary_covers_english_portuguese_and_fails_unknown(self):
        self.assertEqual(
            classify_status("Ratified and Approved by Tripartite Deliberation"),
            STATUS_CANONICAL,
        )
        self.assertEqual(
            classify_status("Ratificado e Aprovado pela Mesa Redonda Tripartite"),
            STATUS_CANONICAL,
        )
        self.assertEqual(classify_status("ACCEPTED"), STATUS_CANONICAL)
        self.assertEqual(classify_status("Official Source of Truth"), STATUS_CANONICAL)
        self.assertEqual(classify_status("ARCHIVED_SUPERSEDED"), STATUS_NON_CANONICAL)
        self.assertEqual(classify_status("Aceito"), STATUS_UNKNOWN)

    def test_ssot_allows_exact_sources_with_one_semantic_identity(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            adr_dir = Path(tmp_dir) / "adr"
            adr_dir.mkdir()
            portuguese = """# Backlog Graph
- **Status:** Ratificado e Aprovado pela Mesa Redonda Tripartite
"""
            english = """# SpecGraph
- **Status:** Ratified and Approved by Tripartite Deliberation
"""
            (adr_dir / "ADR-001_BACKLOG_GRAPH.md").write_text(portuguese, encoding="utf-8")
            (adr_dir / "ADR-001_BACKLOG_GRAPH_deadbeef.md").write_text(portuguese, encoding="utf-8")
            (adr_dir / "ADR-001_SPECGRAPH.md").write_text(english, encoding="utf-8")
            (adr_dir / "ADR-001_SPECGRAPH_b6d508c0.md").write_text(english, encoding="utf-8")

            report = audit_ssot_registry(tmp_dir)

            self.assertTrue(report.is_valid)
            self.assertEqual(report.canonical_documents, 4)

    def test_generic_version_filenames_use_titles_as_semantic_identity(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            adr_dir = Path(tmp_dir) / "adr"
            adr_dir.mkdir()
            status = "\n- **Status:** Ratificado\n"
            (adr_dir / "v001_11111111.md").write_text(
                "# ADR-100: Alpha" + status, encoding="utf-8"
            )
            (adr_dir / "v001_22222222.md").write_text(
                "# ADR-200: Beta" + status, encoding="utf-8"
            )

            report = audit_ssot_registry(tmp_dir)

            self.assertTrue(report.is_valid)

    def test_unknown_explicit_status_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            doc = Path(tmp_dir) / "ADR-777_unknown.md"
            doc.write_text("# Unknown\n- **Status:** Aceito\n", encoding="utf-8")

            report = audit_ssot_registry(tmp_dir)

            self.assertFalse(report.is_valid)
            self.assertEqual(report.unknown_status_documents, ["ADR-777_unknown.md"])
            self.assertIn("Unrecognized status", report.violations[0].description)

    def test_tombstone_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            active_doc = tmp_path / "canonical.md"
            active_doc.write_text("# Active Canonical Doc", encoding="utf-8")

            old_doc = tmp_path / "legacy.md"
            old_doc.write_text("# Legacy Doc", encoding="utf-8")

            # Apply tombstone
            apply_tombstone(old_doc, "canonical.md", "Consolidated into canonical.md")

            # Verify
            res = verify_tombstones(tmp_path)
            self.assertEqual(res.total_tombstones, 1)
            self.assertEqual(res.valid_tombstones, 1)
            self.assertTrue(res.is_healthy)

            ssot = audit_ssot_registry(tmp_path)
            self.assertTrue(ssot.is_valid)
            self.assertEqual(ssot.canonical_documents, 0)

    def test_tombstone_verifier_ignores_mentions_and_requires_pointer(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "discussion.md").write_text(
                "# Discussion\nThe TOMBSTONE and ARCHIVED_SUPERSEDED markers are documented here.\n",
                encoding="utf-8",
            )
            (tmp_path / "broken.md").write_text(
                "# [TOMBSTONE] Broken\n> **Status:** `ARCHIVED_SUPERSEDED`\n",
                encoding="utf-8",
            )

            report = verify_tombstones(tmp_path)

            self.assertEqual(report.total_tombstones, 1)
            self.assertEqual(report.valid_tombstones, 0)
            self.assertEqual(
                report.broken_pointers,
                [("broken.md", "<missing canonical target>")],
            )


if __name__ == "__main__":
    unittest.main()
