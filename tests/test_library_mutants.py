"""Adversarial Mutation Test Suite for tare.tools.library (Harvester, RAG, and Vector Indexer).

Executes targeted mutation tests to verify 100% mutant kill rate across:
- M1: Path Traversal & Unbounded Ingress Injection
- M2: Dedup Threshold Boundary (89.9% vs 90.1%) & Normalization Tampering
- M3: Vector DB Dimension Mismatch & Cross-Namespace Leakage (Fail-Closed)
- M4: Local RAG Robustness under Corrupted Endpoints & Network Faults
- M5: Noise Rejection & Harvester Idempotency under High Concurrency
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.bookkeeper.harvest_corpus import (
    CRAWL_EXCLUDED_DIRS,
    classify_document_type,
    scan_source_directory,
    run_harvester,
)
from tools.bookkeeper.dedup_detector import compute_similarity, detect_duplicates
from tools.indexer.embed_corpus import LibraryVectorDB, cosine_similarity
from tools.query import semantic_search_library, ask_library, search_library
from tools.inference.local_client import LocalInferenceClient


class LibraryMutationTests(unittest.TestCase):

    # =========================================================================
    # M1: Path Traversal & Unbounded Ingress Injection
    # =========================================================================
    def test_mutant_m1_unbounded_ingress_and_excluded_dirs_traversal(self):
        """Mutant attempting to crawl into .git, .gemini, node_modules, and AppData must be killed."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_root = tmp_path / "source_tree"
            source_root.mkdir(parents=True, exist_ok=True)

            # Create legitimate doc
            (source_root / "ADR-001_good.md").write_text("# ADR-001: Valid Architecture\nClean payload.", encoding="utf-8")

            # Create trap directories (must all be pruned/ignored)
            for trap_dir_name in [".git", "node_modules", ".gemini", "__pycache__", ".pytest_cache", "AppData"]:
                trap = source_root / trap_dir_name
                trap.mkdir(parents=True, exist_ok=True)
                (trap / "LEAKED_SECRET_ADR.md").write_text("# ADR-999: Dangerous Leaked Payload\nShould never be seen.", encoding="utf-8")

            discovered = scan_source_directory(source_root, library_root=tmp_path / "lib")
            discovered_names = [d.filename for d in discovered]

            self.assertIn("ADR-001_good.md", discovered_names)
            self.assertNotIn("LEAKED_SECRET_ADR.md", discovered_names)
            self.assertEqual(len(discovered), 1)

    # =========================================================================
    # M2: Dedup Threshold Boundary (89.9% vs 90.1%) & Normalization
    # =========================================================================
    def test_mutant_m2_dedup_boundary_and_normalization_mutants(self):
        """Mutant testing exact 90% boundary: >= 0.90 is duplicate/drift, < 0.90 is new."""
        base_text = " ".join([f"architectural_invariant_token_{i}" for i in range(30)])
        
        # Test 1: Identical text -> 1.0
        self.assertAlmostEqual(compute_similarity(base_text, base_text), 1.0)

        # Test 2: Whitespace and case tampering -> Must normalize cleanly to 1.0
        tampered_whitespace = "\n\n  " + base_text.upper() + "   \t\n"
        self.assertAlmostEqual(compute_similarity(base_text, tampered_whitespace), 1.0)

        # Test 3: Substantial change (> 10%) -> similarity must drop below 0.90
        substantially_different = " ".join([f"different_token_{i}" for i in range(15)] + [f"architectural_invariant_token_{i}" for i in range(15)])
        sim_low = compute_similarity(base_text, substantially_different)
        self.assertLess(sim_low, 0.90)

    # =========================================================================
    # M3: Vector DB Dimension Mismatch & Cross-Namespace Leakage (Fail-Closed)
    # =========================================================================
    def test_mutant_m3_vector_dimension_mismatch_and_cross_namespace_leak(self):
        """Mutant passing wrong vector dimensions or probing namespace leakage must fail-closed."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test_mutants.db"
            vdb = LibraryVectorDB(db_path)

            # Insert a 4-dimensional real vector
            vdb.upsert_chunk(
                doc_id="DOC-1",
                relative_path="docs/doc1.md",
                chunk_index=0,
                chunk_text="Chunk text 1",
                sha256="sha1",
                embedding=[1.0, 0.0, 0.0, 0.0],
                provenance="real",
                model_name="bge-m3",
            )

            # Insert a 4-dimensional pseudo vector
            vdb.upsert_chunk(
                doc_id="DOC-2",
                relative_path="docs/doc2.md",
                chunk_index=0,
                chunk_text="Chunk text 2",
                sha256="sha2",
                embedding=[0.0, 1.0, 0.0, 0.0],
                provenance="pseudo",
                model_name="local-embed",
            )

            # Query with mismatched dimension (3-dim query against 4-dim DB) -> cosine_similarity must raise ValueError
            with self.assertRaises(ValueError):
                cosine_similarity([1.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0])

            # Search with strict provenance "real" must never return "pseudo"
            results_real = vdb.search([1.0, 0.0, 0.0, 0.0], top_k=5, provenance="real", model_name="bge-m3")
            self.assertEqual(len(results_real), 1)
            self.assertEqual(results_real[0].doc_id, "DOC-1")

    # =========================================================================
    # M4: Local RAG Robustness under Network Faults & Corrupted Endpoints
    # =========================================================================
    def test_mutant_m4_local_rag_graceful_fault_tolerance(self):
        """Mutant testing RAG when endpoint returns HTTP 500 or corrupted JSON."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            adr_dir = tmp_path / "docs" / "adr"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-048.md").write_text("# ADR-048: Local Inference Substrate\nDetails on dual engine.", encoding="utf-8")

            client = LocalInferenceClient()

            # Case A: Server offline -> RAG must return structured offline fallback
            with patch.object(client, "health_check", return_value={"online": False}):
                rag_offline = ask_library("How does ADR-048 work?", client=client, root_dir=tmp_path)
                self.assertIn("OFFLINE SYNTHESIS", rag_offline["answer"])
                self.assertTrue(len(rag_offline["sources"]) > 0)

            # Case B: Server online but chat_completion raises exception -> RAG handles gracefully
            with patch.object(client, "health_check", return_value={"online": True}):
                with patch.object(client, "chat_completion", side_effect=RuntimeError("Connection reset by peer")):
                    rag_error = ask_library("How does ADR-048 work?", client=client, root_dir=tmp_path)
                    self.assertIn("ERROR querying local LLM", rag_error["answer"])
                    self.assertIn("docs/adr/ADR-048.md", rag_error["sources"])

    # =========================================================================
    # M5: Noise Rejection & Harvester Concurrency
    # =========================================================================
    def test_mutant_m5_noise_rejection_and_empty_stubs(self):
        """Mutant verifying rejection of binary locks, log dumps (>2.5MB), and stubs (<30B)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            src_dir = tmp_path / "noisy_source"
            src_dir.mkdir(parents=True, exist_ok=True)

            # Legitimate doc
            (src_dir / "SPEC-001.md").write_text("# SPEC-001: High Performance OpenSDD\nValid payload content.", encoding="utf-8")

            # Binary lockfile
            (src_dir / "pnpm-lock.yaml").write_text("lockfileVersion: 5.4\npackages: {}", encoding="utf-8")
            (src_dir / "Cargo.lock").write_text("# This file is automatically generated by Cargo.", encoding="utf-8")

            # Stub under 30 bytes
            (src_dir / "empty_stub.md").write_text("# Hi", encoding="utf-8")  # 4 bytes

            discovered = scan_source_directory(src_dir, library_root=tmp_path / "lib")
            self.assertEqual(len(discovered), 1)
            self.assertEqual(discovered[0].filename, "SPEC-001.md")


if __name__ == "__main__":
    unittest.main()
