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
from tools.bookkeeper.ssot_registry import audit_ssot_registry
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


if __name__ == "__main__":
    unittest.main()
