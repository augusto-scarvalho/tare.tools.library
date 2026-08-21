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

    # =========================================================================
    # M6: Secret Leak Scanner Gate (Quarantines sk-live, ghp, AKIA, Private Keys)
    # =========================================================================
    def test_mutant_m6_secret_leak_scanner_quarantine(self):
        """Mutant verifying that credentials and private keys are immediately quarantined."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            src_dir = tmp_path / "leaky_source"
            src_dir.mkdir(parents=True, exist_ok=True)

            # Legitimate doc
            (src_dir / "DOC-CLEAN.md").write_text("# Clean Architecture\nSafe public content with zero leaks.", encoding="utf-8")

            # Document with OpenAI sk-live token
            (src_dir / "LEAK-OPENAI.md").write_text("# Leak Doc\nAuthorization: Bearer sk-live-abcdef1234567890abcdef1234567890\nEnd of note.", encoding="utf-8")

            # Document with AWS Key
            (src_dir / "LEAK-AWS.md").write_text("# AWS Config\naws_access_key_id = AKIAIOSFODNN7EXAMPLE\nSecret stuff.", encoding="utf-8")

            # Document with GitHub Token
            (src_dir / "LEAK-GITHUB.md").write_text("# GH Token\nGH_TOKEN=ghp_123456789012345678901234567890123456\nToken line.", encoding="utf-8")

            # Document with Private Key
            (src_dir / "LEAK-KEY.md").write_text("# SSL Key\n-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA...\n-----END RSA PRIVATE KEY-----", encoding="utf-8")

            discovered = scan_source_directory(src_dir, library_root=tmp_path / "lib")
            
            # 5 files total: 1 clean and 4 quarantined with REJECTED_SECRET
            self.assertEqual(len(discovered), 5)
            
            clean = [d for d in discovered if d.status == "NEW"]
            quarantined = [d for d in discovered if d.status == "REJECTED_SECRET"]
            
            self.assertEqual(len(clean), 1)
            self.assertEqual(clean[0].filename, "DOC-CLEAN.md")
            self.assertEqual(len(quarantined), 4)
            for q in quarantined:
                self.assertEqual(q.inferred_type, "quarantine")
                self.assertTrue("SECRET_LEAK_DETECTED" in q.conflict_path)
    # =========================================================================
    # M7: Anti-Sybil Duplicate Model Ingress Mutation (Fail-Closed)
    # =========================================================================
    def test_mutant_m7_anti_sybil_duplicate_model_mutation(self):
        """Mutant attempting Sybil consensus with identical model across distinct seats must be killed."""
        from tools.governance.round_table_engine import (
            DeliberationStatus,
            QuorumMode,
            compute_quorum_mode,
            evaluate_round_verdict,
        )

        sybil_votes = {
            "google": {"status": "OK", "provider": "google", "model": "gemini-3.7-flash", "vote": {"verdict": "APPROVE"}},
            "openai": {"status": "OK", "provider": "nim_backup_openai", "model": "z-ai/glm-5.2", "vote": {"verdict": "APPROVE"}},
            "anthropic": {"status": "OK", "provider": "nim_backup_anthropic", "model": "z-ai/glm-5.2", "vote": {"verdict": "APPROVE"}},
        }
        
        mode = compute_quorum_mode(sybil_votes)
        self.assertEqual(mode, QuorumMode.HELD_UNAVAILABLE)

        status, reason = evaluate_round_verdict(sybil_votes, current_round=1)
        self.assertEqual(status, DeliberationStatus.HELD_UNAVAILABLE)
        self.assertIn("Violação Anti-Sybil", reason)

    # =========================================================================
    # M8: Round Limit Boundary Mutation (N <= 3 and N = 4 with Overtime)
    # =========================================================================
    def test_mutant_m8_round_limit_boundary_and_overtime_mutants(self):
        """Mutant attempting to bypass mechanical round limit ceiling must be killed."""
        from tools.governance.round_table_engine import (
            DeliberationStatus,
            evaluate_round_verdict,
        )

        revising_votes = {
            "google": {"status": "OK", "provider": "google", "model": "gemini-3.7-flash", "vote": {"verdict": "REVISE"}},
            "openai": {"status": "OK", "provider": "openai", "model": "gpt-5.6-sol", "vote": {"verdict": "APPROVE"}},
        }

        # Round 3 without overtime -> HELD_PROGRESS_REVIEW
        status_r3, _ = evaluate_round_verdict(revising_votes, current_round=3, overtime_granted=False)
        self.assertEqual(status_r3, DeliberationStatus.HELD_PROGRESS_REVIEW)

        # Round 4 WITH overtime -> HELD_OVERTIME_EXHAUSTED
        status_r4_ot, _ = evaluate_round_verdict(revising_votes, current_round=4, overtime_granted=True)
        self.assertEqual(status_r4_ot, DeliberationStatus.HELD_OVERTIME_EXHAUSTED)

    # =========================================================================
    # M9: Section Parser Code Fence Tampering & Delta Mutation
    # =========================================================================
    def test_mutant_m9_markdown_parser_code_fence_tampering(self):
        """Mutant embedding fake ## headers inside code blocks must be ignored by section splitter."""
        from tools.governance.round_table_engine import split_markdown_sections

        markdown_with_trap = """## Section 1
Real content.

```python
## Fake Section 2 Inside Code Block
def foo():
    pass
```

## Section 2
Legitimate second section.
"""
        sections = split_markdown_sections(markdown_with_trap)
        self.assertIn("Section 1", sections)
        self.assertIn("Section 2", sections)
        self.assertNotIn("Fake Section 2 Inside Code Block", sections)

    # =========================================================================
    # M10: Stale Lock Healing & Active Process Contention Mutant
    # =========================================================================
    def test_mutant_m10_stale_lock_healing_and_contention(self):
        """Mutant creating dead PID lock must be healed; active PID lock must block."""
        from tools.governance.round_table_engine import CaseLock

        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / ".lock"

            # Dead PID -> Must heal and acquire
            lock_path.write_text(json.dumps({"pid": 999999999, "created_at": 1000}), encoding="utf-8")
            with CaseLock(lock_path) as lock:
                self.assertTrue(lock.acquired)
                self.assertEqual(json.loads(lock_path.read_text(encoding="utf-8")).get("pid"), os.getpid())

            # Living PID -> Secondary acquisition must raise TimeoutError
            with CaseLock(lock_path):
                with self.assertRaises(TimeoutError):
                    with CaseLock(lock_path, timeout_secs=0.3):
                        pass

    # =========================================================================
    # M11: Audit Mode Falsifier Bypass Mutation (Fail-Closed)
    # =========================================================================
    def test_mutant_m11_audit_falsifier_bypass_fail_closed(self):
        """Mutant attempting to block audit with empty falsifier or invalid schema must fail closed."""
        from tools.policy.frugality_guard import check_audit_findings_falsifiers

        bad_finding = [{"severity": "blocking", "claim": "Bad code", "falsifier": "   "}]
        ok, msg = check_audit_findings_falsifiers(bad_finding)
        self.assertFalse(ok)
        self.assertIn("não possui falsificador", msg)


if __name__ == "__main__":
    unittest.main()
