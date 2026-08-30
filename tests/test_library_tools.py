"""Unit tests for tools in tare.tools.library (ingest, manifest builder, query)."""

import hashlib
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
from tools.build_manifest import (
    AUTHORITY_DECLARED,
    AUTHORITY_EXCLUDED,
    AUTHORITY_UNMANAGED,
    build_library_manifest,
    save_manifest,
)
from tools.bookkeeper.tombstone_manager import apply_tombstone
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

    def test_ingest_duplicate_boundary_90_percent(self):
        from tools.ingest import compute_similarity
        from unittest.mock import patch
        words_base = [f"token{i}" for i in range(25)]
        words_90 = list(words_base)
        words_90[-1] = "differenttoken"  # alters last shingle
        
        sim_high = compute_similarity(" ".join(words_base), " ".join(words_90))
        self.assertGreaterEqual(sim_high, 0.90)

        # Alter 5 shingles -> below 0.90
        words_low = list(words_base)
        for j in range(20, 25):
            words_low[j] = f"changed{j}"
        sim_low = compute_similarity(" ".join(words_base), " ".join(words_low))
        self.assertLess(sim_low, 0.90)

        # End-to-end ingest gate validation:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dest_dir = tmp_path / "docs" / "adr"
            dest_dir.mkdir(parents=True, exist_ok=True)
            (dest_dir / "ADR-001.md").write_text(" ".join(words_base), encoding="utf-8")

            # Document with exactly sim >= 0.90 must be rejected
            src_file_90 = tmp_path / "incoming_90.md"
            src_file_90.write_text(" ".join(words_90), encoding="utf-8")
            with patch("tools.ingest.compute_similarity", return_value=0.90):
                res_90 = ingest_document(src_file_90, doc_type="adr", root_dir=tmp_path)
            self.assertFalse(res_90.success)
            self.assertTrue(res_90.is_duplicate)

            # Document with sim < 0.90 must be accepted
            src_file_low = tmp_path / "incoming_low.md"
            src_file_low.write_text(" ".join(words_low), encoding="utf-8")
            res_low = ingest_document(src_file_low, doc_type="adr", root_dir=tmp_path)
            self.assertTrue(res_low.success)
            self.assertFalse(res_low.is_duplicate)

    def test_ingest_force_preserves_existing_file_non_destructive(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dest_dir = tmp_path / "docs" / "adr"
            dest_dir.mkdir(parents=True, exist_ok=True)
            existing_file = dest_dir / "ADR-001.md"
            existing_file.write_text("ORIGINAL CONTENT", encoding="utf-8")

            # Ingest new file with same target name using force=True
            src_file = tmp_path / "ADR-001.md"
            src_file.write_text("DIFFERENT CONTENT", encoding="utf-8")

            res = ingest_document(src_file, doc_type="adr", force=True, root_dir=tmp_path)
            self.assertTrue(res.success)
            # Original file MUST NOT be destroyed
            self.assertEqual(existing_file.read_text(encoding="utf-8"), "ORIGINAL CONTENT")
            # Ingested file gets a non-colliding suffixed name
            self.assertNotEqual(res.target_path, existing_file)
            self.assertTrue(res.target_path.exists())
            self.assertEqual(res.target_path.read_text(encoding="utf-8"), "DIFFERENT CONTENT")

    def test_ingest_concurrent_collision_preserves_both_payloads(self):
        import concurrent.futures
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Prepare two distinct sources with same target filename
            src_a = tmp_path / "src_a" / "ADR-099.md"
            src_a.parent.mkdir(parents=True, exist_ok=True)
            src_a.write_text("PAYLOAD_ALPHA_12345", encoding="utf-8")

            src_b = tmp_path / "src_b" / "ADR-099.md"
            src_b.parent.mkdir(parents=True, exist_ok=True)
            src_b.write_text("PAYLOAD_BETA_67890", encoding="utf-8")

            # Execute simultaneous ingests
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                f_a = executor.submit(ingest_document, src_a, doc_type="adr", force=True, root_dir=tmp_path)
                f_b = executor.submit(ingest_document, src_b, doc_type="adr", force=True, root_dir=tmp_path)
                res_a = f_a.result()
                res_b = f_b.result()

            self.assertTrue(res_a.success)
            self.assertTrue(res_b.success)
            self.assertTrue(res_a.target_path.exists())
            self.assertTrue(res_b.target_path.exists())
            self.assertNotEqual(res_a.target_path, res_b.target_path)
            # Verify both payloads are fully preserved byte-for-byte
            self.assertEqual(res_a.target_path.read_text(encoding="utf-8"), "PAYLOAD_ALPHA_12345")
            self.assertEqual(res_b.target_path.read_text(encoding="utf-8"), "PAYLOAD_BETA_67890")

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
            self.assertEqual(manifest.version, "3.0.0")
            self.assertEqual(manifest.adrs[0].id, manifest.adrs[0].sha256)
            self.assertEqual(manifest.adrs[0].authority_state, AUTHORITY_EXCLUDED)
            self.assertEqual(manifest.specs[0].authority_state, AUTHORITY_UNMANAGED)
            self.assertEqual(manifest.projection_receipt["source_count"], 2)

            out_file = save_manifest(manifest, root_dir=tmp_path)
            self.assertTrue(out_file.exists())
            loaded = json.loads(out_file.read_text(encoding="utf-8"))
            self.assertEqual(loaded["total_documents"], 2)

    def test_atomic_manifest_publication(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            manifest = build_library_manifest(root_dir=tmp_path)
            with patch("os.fsync") as mock_fsync:
                out_file = save_manifest(manifest, root_dir=tmp_path)
                self.assertTrue(out_file.exists())
                self.assertTrue(mock_fsync.called)
            # Ensure no residual .tmp files exist in catalog/
            tmp_files = list((tmp_path / "catalog").glob("*.tmp"))
            self.assertEqual(len(tmp_files), 0)

    def test_manifest_ids_are_content_addressed_and_globally_unique(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            adr_dir = tmp_path / "docs" / "adr"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "DECISION_a1b2c3d4.md").write_text(
                "# First decision", encoding="utf-8"
            )
            (adr_dir / "DECISION_e5f6a7b8.md").write_text(
                "# Second decision", encoding="utf-8"
            )
            spec_dir = tmp_path / "specs"
            spec_dir.mkdir()
            (spec_dir / "DECISION_a1b2c3d4.md").write_text(
                "# Specification with colliding stem", encoding="utf-8"
            )

            manifest = build_library_manifest(root_dir=tmp_path)

            self.assertEqual(manifest.version, "3.0.0")
            all_ids = [
                entry.id for entry in manifest.adrs + manifest.specs
            ]
            self.assertEqual(len(all_ids), len(set(all_ids)))
            self.assertTrue(all(entry.id == entry.sha256 for entry in manifest.adrs))

    def test_manifest_consolidates_active_canonical_exact_copy(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            adr_dir = Path(tmp_dir) / "docs" / "adr"
            adr_dir.mkdir(parents=True)
            content = """# ADR-100: Canonical
- **Status:** Ratificado e Aprovado pela Mesa Redonda Tripartite
Targets tare.tools.specgraph.
"""
            (adr_dir / "ADR-100_TEST.md").write_text(content, encoding="utf-8")
            (adr_dir / "ADR-100_TEST_deadbeef.md").write_text(content, encoding="utf-8")

            manifest = build_library_manifest(root_dir=tmp_dir)

            self.assertEqual(len(manifest.adrs), 1)
            self.assertEqual(manifest.adrs[0].authority_state, AUTHORITY_DECLARED)
            self.assertEqual(len(manifest.adrs[0].source_paths), 2)
            self.assertEqual(
                manifest.projection_receipt["exact_groups_consolidated"], 1
            )
            self.assertEqual(
                manifest.adrs[0].relative_path,
                "docs/adr/ADR-100_TEST.md",
            )

    def test_manifest_rejects_distinct_bytes_with_same_active_semantic_id(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            adr_dir = Path(tmp_dir) / "docs" / "adr"
            adr_dir.mkdir(parents=True)
            status = "\n- **Status:** Ratified and Approved by Tripartite Deliberation\n"
            (adr_dir / "ADR-101_TEST.md").write_text(
                "# First" + status, encoding="utf-8"
            )
            (adr_dir / "ADR-101_TEST_cafebabe.md").write_text(
                "# Second" + status, encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "semantic document ID 'ADR-101_TEST'"):
                build_library_manifest(root_dir=tmp_dir)

    def test_manifest_tombstone_preserves_source_without_grounding_authority(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            adr_dir = Path(tmp_dir) / "docs" / "adr"
            adr_dir.mkdir(parents=True)
            canonical = adr_dir / "ADR-102_TEST.md"
            canonical.write_text(
                "# ADR-102\n- **Status:** Ratificado e Aprovado\n"
                "Applies to tare.tools.specgraph.\n",
                encoding="utf-8",
            )
            redundant = adr_dir / "ADR-102_TEST_deadbeef.md"
            redundant.write_bytes(canonical.read_bytes())
            apply_tombstone(
                redundant,
                "adr/ADR-102_TEST.md",
                "Exact duplicate disposition under ADR-059",
            )

            manifest = build_library_manifest(root_dir=tmp_dir)
            by_path = {entry.relative_path: entry for entry in manifest.adrs}

            self.assertEqual(manifest.canonical_ssot_count, 1)
            self.assertEqual(
                by_path["docs/adr/ADR-102_TEST.md"].target_repositories,
                ["tare.tools.specgraph"],
            )
            tombstone = by_path["docs/adr/ADR-102_TEST_deadbeef.md"]
            self.assertEqual(tombstone.status, "ARCHIVED_SUPERSEDED")
            self.assertEqual(tombstone.authority_state, AUTHORITY_EXCLUDED)
            self.assertEqual(tombstone.target_repositories, [])

    def test_manifest_unknown_status_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            adr_dir = Path(tmp_dir) / "docs" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-103_UNKNOWN.md").write_text(
                "# Unknown\n- **Status:** Aceito\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "unrecognized document status"):
                build_library_manifest(root_dir=tmp_dir)

    def test_manifest_consolidates_specs_and_preserves_ordered_provenance(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            spec_dir = Path(tmp_dir) / "specs"
            spec_dir.mkdir(parents=True)
            content = "# SPEC-200: One payload\nTargets tare.tools.specgraph.\n"
            (spec_dir / "SPEC-200.md").write_text(content, encoding="utf-8")
            (spec_dir / "SPEC-200_deadbeef.md").write_text(content, encoding="utf-8")

            manifest = build_library_manifest(root_dir=tmp_dir)

            self.assertEqual(len(manifest.specs), 1)
            entry = manifest.specs[0]
            self.assertEqual(
                entry.id,
                hashlib.sha256((spec_dir / "SPEC-200.md").read_bytes()).hexdigest(),
            )
            self.assertEqual(entry.authority_state, AUTHORITY_UNMANAGED)
            self.assertEqual(
                [source.relative_path for source in entry.source_paths],
                ["specs/SPEC-200.md", "specs/SPEC-200_deadbeef.md"],
            )
            self.assertEqual(
                manifest.projection_receipt["consolidated_source_count"], 1
            )

    def test_manifest_mixed_exact_group_preserves_per_source_authority(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            adr_dir = root / "docs" / "adr"
            spec_dir = root / "specs"
            adr_dir.mkdir(parents=True)
            spec_dir.mkdir()
            content = (
                "# Shared\n- **Status:** Ratified\n"
                "Targets tare.tools.specgraph.\n"
            )
            (adr_dir / "ADR-201_SHARED.md").write_text(content, encoding="utf-8")
            (spec_dir / "SPEC-201_SHARED.md").write_text(content, encoding="utf-8")

            manifest = build_library_manifest(root_dir=root)
            entries = manifest.adrs + manifest.specs

            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].authority_state, AUTHORITY_DECLARED)
            self.assertEqual(
                {source.authority_state for source in entries[0].source_paths},
                {AUTHORITY_DECLARED, AUTHORITY_UNMANAGED},
            )
            self.assertEqual(manifest.projection_receipt["mixed_state_groups"], 1)

    def test_manifest_serialization_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            spec_dir = root / "specs"
            spec_dir.mkdir(parents=True)
            (spec_dir / "SPEC-A.md").write_text("# A", encoding="utf-8")

            first = save_manifest(build_library_manifest(root), root).read_bytes()
            second = save_manifest(build_library_manifest(root), root).read_bytes()

            self.assertEqual(first, second)

    def test_manifest_rejects_broken_tombstone_before_publication(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            adr_dir = Path(tmp_dir) / "docs" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-202_OLD.md").write_text(
                "# [TOMBSTONE] Broken\n"
                "> **Canônico:** [missing](adr/missing.md)\n"
                "> **Status:** `ARCHIVED_SUPERSEDED`\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "broken tombstone"):
                build_library_manifest(root_dir=tmp_dir)

    def test_vector_db_wal_mode_active(self):
        from tools.indexer.embed_corpus import LibraryVectorDB
        import sqlite3
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = Path(tmp_dir) / "test_wal.db"
            vdb = LibraryVectorDB(db_file)
            conn = sqlite3.connect(vdb.db_path)
            try:
                mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
                self.assertEqual(mode.lower(), "wal")
            finally:
                conn.close()

    def test_ingest_fallback_exclusive_creation(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            src_file = tmp_path / "test_doc.md"
            src_file.write_text("SOME CONTENT", encoding="utf-8")
            dest_dir = tmp_path / "docs" / "adr"
            dest_dir.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256("SOME CONTENT".encode("utf-8")).hexdigest()
            # Pre-create candidate collision files to exhaust candidate list and force line 144 fallback
            (dest_dir / "test_doc.md").write_text("C1", encoding="utf-8")
            (dest_dir / f"test_doc_{digest[:8]}.md").write_text("C2", encoding="utf-8")
            (dest_dir / f"test_doc_{digest[:12]}.md").write_text("C3", encoding="utf-8")
            fallback = dest_dir / f"test_doc_{digest[:8]}_1234567890000.md"
            fallback.write_text("C4", encoding="utf-8")

            with patch("time.time", return_value=1234567890):
                with self.assertRaises(FileExistsError):
                    ingest_document(src_file, doc_type="adr", force=True, root_dir=tmp_path)
            self.assertEqual(fallback.read_text(encoding="utf-8"), "C4")

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

    def test_domain_ontology_lookup(self):
        from tools.query import lookup_concept
        res = lookup_concept("CASPersistence")
        self.assertIsNotNone(res)
        self.assertIn("CASPersistence", res["id"])

    def test_vector_db_lifecycle(self):
        from tools.indexer.embed_corpus import LibraryVectorDB, cosine_similarity
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = Path(tmp_dir) / "test_vec.db"
            vdb = LibraryVectorDB(db_file)
            self.assertEqual(vdb.count_chunks(), 0)

            vdb.upsert_chunk(
                doc_id="DOC-1",
                relative_path="docs/doc1.md",
                chunk_index=0,
                chunk_text="CAS state machine",
                sha256="abc123",
                embedding=[1.0, 0.0, 0.0],
            )
            self.assertEqual(vdb.count_chunks(), 1)

            matches = vdb.search([1.0, 0.0, 0.0], top_k=1)
            self.assertEqual(len(matches), 1)
            self.assertAlmostEqual(matches[0].score, 1.0)

    def test_vector_dimension_mismatch_fail_closed(self):
        from tools.indexer.embed_corpus import cosine_similarity, LibraryVectorDB
        # cosine_similarity must raise ValueError on length mismatch
        with self.assertRaises(ValueError):
            cosine_similarity([1.0, 0.0], [1.0, 0.0, 0.0])

        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = Path(tmp_dir) / "test_vec2.db"
            vdb = LibraryVectorDB(db_file)
            vdb.upsert_chunk(
                doc_id="DOC-1",
                relative_path="docs/doc1.md",
                chunk_index=0,
                chunk_text="Chunk 1",
                sha256="abc",
                embedding=[1.0, 0.0],
                provenance="pseudo",
            )
            # Searching with 3-dimensional query must fail-safe skip 2-dimensional chunks
            results = vdb.search([1.0, 0.0, 0.0], top_k=5)
            self.assertEqual(len(results), 0)

    def test_local_inference_client_offline_graceful(self):
        from tools.inference.local_client import LocalInferenceClient, LocalInferenceConfig
        # Pointing to unroutable port must fail gracefully without crash
        client = LocalInferenceClient(LocalInferenceConfig(host="http://127.0.0.1:59999", timeout_seconds=1.0))
        status = client.health_check()
        self.assertFalse(status["online"])
        self.assertIn("error", status)

    def test_local_inference_client_readiness_check(self):
        from tools.inference.local_client import LocalInferenceClient, LocalInferenceConfig
        client = LocalInferenceClient(LocalInferenceConfig(host="http://127.0.0.1:59999", timeout_seconds=1.0))
        res = client.readiness_check(required_model="qwen2.5-coder")
        self.assertFalse(res["ready"])
        self.assertIn("error", res)

    def test_local_inference_client_readiness_check_cuda_fail_closed(self):
        from tools.inference.local_client import LocalInferenceClient, LocalInferenceConfig
        from unittest.mock import patch, MagicMock
        client = LocalInferenceClient(LocalInferenceConfig(host="http://127.0.0.1:59999", timeout_seconds=1.0))
        res = client.readiness_check(require_cuda=True)
        self.assertFalse(res["ready"])
        self.assertIn("error", res)

        # Mock server online with 0 GPU layers (CPU mode) -> must fail closed
        with patch.object(client, "health_check", return_value={"online": True, "models": [{"id": "m1"}]}):
            with patch("urllib.request.urlopen") as mock_open:
                mock_resp = MagicMock()
                mock_resp.read.return_value = json.dumps({"n_gpu_layers": 0, "device": "cuda"}).encode("utf-8")
                mock_resp.__enter__.return_value = mock_resp
                mock_open.return_value = mock_resp
                res = client.readiness_check(required_model="m1", require_cuda=True)
                self.assertFalse(res["ready"])
                self.assertIn("CPU-only mode", res["error"])

        # Mock server online with device: 'cpu' -> must fail closed
        with patch.object(client, "health_check", return_value={"online": True, "models": [{"id": "m1"}]}):
            with patch("urllib.request.urlopen") as mock_open:
                mock_resp = MagicMock()
                mock_resp.read.return_value = json.dumps({"n_gpu_layers": 32, "device": "cpu"}).encode("utf-8")
                mock_resp.__enter__.return_value = mock_resp
                mock_open.return_value = mock_resp
                res = client.readiness_check(required_model="m1", require_cuda=True)
                self.assertFalse(res["ready"])
                self.assertIn("CPU-only mode", res["error"])

    def test_local_inference_client_readiness_check_model_mismatch_fail_closed(self):
        from tools.inference.local_client import LocalInferenceClient
        from unittest.mock import patch
        client = LocalInferenceClient()
        # Mock server reporting model B loaded on CUDA, but client requires model A
        with patch.object(client, "health_check", return_value={"online": True, "models": [{"id": "model-B"}]}):
            with patch("urllib.request.urlopen"):
                res = client.readiness_check(required_model="model-A", require_cuda=False)
                self.assertFalse(res["ready"])
                self.assertIn("not found in loaded models", res["error"])

    def test_ingest_canonical_normalization_markdown_links_symmetry(self):
        from tools.bookkeeper.dedup_detector import detect_duplicates
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dest_dir = tmp_path / "docs" / "adr"
            dest_dir.mkdir(parents=True, exist_ok=True)
            doc_a = dest_dir / "ADR-100.md"
            doc_a.write_text("# Decision Record\nAlpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi.", encoding="utf-8")

            # Doc B has same body text but wrapping tokens in markdown links
            doc_b = tmp_path / "ADR-101.md"
            doc_b.write_text("# Decision Record\n[Alpha](https://example.com/a) [beta](https://example.com/b) [gamma](https://example.com/g) [delta](https://example.com/d) [epsilon](https://example.com/e) zeta eta theta iota kappa lambda mu nu xi.", encoding="utf-8")

            # Ingest must reject doc_b as near duplicate
            res = ingest_document(doc_b, doc_type="adr", root_dir=tmp_path)
            self.assertFalse(res.success)
            self.assertTrue(res.is_duplicate)

            # Bookkeeper audit must also see the exact same duplicate relation
            # write doc_b temporarily into acervo to audit
            (dest_dir / "ADR-101.md").write_text(doc_b.read_text(encoding="utf-8"), encoding="utf-8")
            report = detect_duplicates(tmp_path, similarity_threshold=0.85)
            self.assertFalse(report.is_clean)

    def test_vector_db_model_and_provenance_namespace_isolation(self):
        from tools.indexer.embed_corpus import LibraryVectorDB
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = Path(tmp_dir) / "test_namespace.db"
            vdb = LibraryVectorDB(db_file)
            # Upsert two chunks with identical dimensions (3-dim) but different models / provenance
            vdb.upsert_chunk(
                doc_id="DOC-PSEUDO",
                relative_path="docs/pseudo.md",
                chunk_index=0,
                chunk_text="Pseudo vector chunk",
                sha256="hash1",
                embedding=[1.0, 0.0, 0.0],
                provenance="pseudo",
                model_name="pseudo-hash",
            )
            vdb.upsert_chunk(
                doc_id="DOC-REAL",
                relative_path="docs/real.md",
                chunk_index=0,
                chunk_text="Real vector chunk",
                sha256="hash2",
                embedding=[1.0, 0.0, 0.0],
                provenance="real",
                model_name="bge-small-en",
            )
            # Querying with provenance='real' and model_name='bge-small-en' must return only DOC-REAL
            real_results = vdb.search([1.0, 0.0, 0.0], top_k=5, provenance="real", model_name="bge-small-en")
            self.assertEqual(len(real_results), 1)
            self.assertEqual(real_results[0].doc_id, "DOC-REAL")

    def test_agents_md_protocol_compliance(self):
        agents_file = ROOT / "AGENTS.md"
        self.assertTrue(agents_file.exists())
        content = agents_file.read_text(encoding="utf-8")
        self.assertIn("Protocolo 1: Pre-Task Grounding", content)
        self.assertIn("Protocolo 2: Ingestão Automatizada", content)
        self.assertIn("Protocolo 3: Sincronização do Manifesto", content)
        self.assertIn("Protocolo 4: Auditoria de Higiene Documental", content)
    def test_inference_contracts_and_canonical_fixtures(self):
        from tools.inference.contracts import (
            validate_props_payload,
            validate_models_payload,
            CANONICAL_FIXTURE_PROPS_CUDA,
            CANONICAL_FIXTURE_PROPS_CPU_INVALID,
            CANONICAL_FIXTURE_MODELS,
            LlamaServerProps,
            ModelsResponse,
        )
        # 1. Validate CUDA fixture
        props_cuda = validate_props_payload(CANONICAL_FIXTURE_PROPS_CUDA)
        self.assertIsInstance(props_cuda, LlamaServerProps)
        self.assertTrue(props_cuda.is_cuda_accelerated())
        self.assertEqual(props_cuda.n_gpu_layers, 99)
        self.assertEqual(props_cuda.device, "cuda")

        # 2. Validate CPU invalid fixture
        props_cpu = validate_props_payload(CANONICAL_FIXTURE_PROPS_CPU_INVALID)
        self.assertIsInstance(props_cpu, LlamaServerProps)
        self.assertFalse(props_cpu.is_cuda_accelerated())

        # 3. Validate Models fixture
        models = validate_models_payload(CANONICAL_FIXTURE_MODELS)
        self.assertIsInstance(models, ModelsResponse)
        self.assertTrue(models.contains_model("qwen2.5-coder-32b-instruct"))
        self.assertTrue(models.contains_model("bge-large-en-v1.5"))
        self.assertFalse(models.contains_model("non-existent-model"))

        # 4. Error validation on bad payloads
        with self.assertRaises(ValueError):
            validate_props_payload({"device": "cuda"})  # missing n_gpu_layers
        with self.assertRaises(ValueError):
            validate_models_payload({"data": "not-a-list"})

    def test_local_inference_readiness_with_canonical_fixtures(self):
        from tools.inference.local_client import LocalInferenceClient
        from tools.inference.contracts import (
            CANONICAL_FIXTURE_PROPS_CUDA,
            CANONICAL_FIXTURE_PROPS_CPU_INVALID,
            CANONICAL_FIXTURE_MODELS,
        )
        from unittest.mock import patch, MagicMock

        client = LocalInferenceClient()

        # Test against Canonical CUDA + Models fixtures -> Must pass readiness
        with patch.object(client, "health_check", return_value={"online": True, "models": CANONICAL_FIXTURE_MODELS["data"]}):
            with patch("urllib.request.urlopen") as mock_open:
                mock_resp = MagicMock()
                mock_resp.read.return_value = json.dumps(CANONICAL_FIXTURE_PROPS_CUDA).encode("utf-8")
                mock_resp.__enter__.return_value = mock_resp
                mock_open.return_value = mock_resp

                res = client.readiness_check(
                    required_model="qwen2.5-coder-32b-instruct",
                    require_cuda=True,
                )
                self.assertTrue(res["ready"])

        # Test against Canonical CPU fixture -> Must fail closed
        with patch.object(client, "health_check", return_value={"online": True, "models": CANONICAL_FIXTURE_MODELS["data"]}):
            with patch("urllib.request.urlopen") as mock_open:
                mock_resp = MagicMock()
                mock_resp.read.return_value = json.dumps(CANONICAL_FIXTURE_PROPS_CPU_INVALID).encode("utf-8")
                mock_resp.__enter__.return_value = mock_resp
                mock_open.return_value = mock_resp

                res = client.readiness_check(
                    required_model="qwen2.5-coder-32b-instruct",
                    require_cuda=True,
                )
                self.assertFalse(res["ready"])
                self.assertIn("CPU-only mode", res["error"])

    def test_vector_db_high_concurrency_and_idempotence(self):
        import concurrent.futures
        from tools.indexer.embed_corpus import LibraryVectorDB

        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = Path(tmp_dir) / "test_concurrent.db"
            vdb = LibraryVectorDB(db_file)

            def worker_insert(chunk_id: int):
                vdb.upsert_chunk(
                    doc_id=f"DOC-{chunk_id}",
                    relative_path=f"docs/doc_{chunk_id}.md",
                    chunk_index=0,
                    chunk_text=f"Concurrent payload content for chunk {chunk_id}",
                    sha256=f"sha_{chunk_id}",
                    embedding=[float(chunk_id % 10), 1.0, 2.0],
                    provenance="real",
                    model_name="local-embed",
                )
                return chunk_id

            # Run 40 concurrent inserts across 8 worker threads
            num_chunks = 40
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(worker_insert, i) for i in range(num_chunks)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            self.assertEqual(len(results), num_chunks)
            self.assertEqual(vdb.count_chunks(), num_chunks)

            # Re-run the exact same inserts concurrently to verify 100% idempotence under concurrency
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(worker_insert, i) for i in range(num_chunks)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]

            self.assertEqual(vdb.count_chunks(), num_chunks)

    def test_vector_db_atomic_document_upsert(self):
        from tools.indexer.embed_corpus import LibraryVectorDB

        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = Path(tmp_dir) / "test_atomic_doc.db"
            vdb = LibraryVectorDB(db_file)

            chunks_v1 = [
                (0, "Paragraph 1 v1", "sha1", [1.0, 0.0]),
                (1, "Paragraph 2 v1", "sha2", [0.0, 1.0]),
                (2, "Paragraph 3 v1", "sha3", [0.5, 0.5]),
            ]
            ok = vdb.upsert_document_chunks(
                doc_id="DOC-ATOMIC",
                relative_path="docs/atomic.md",
                chunks=chunks_v1,
                provenance="real",
                model_name="local-embed",
            )
            self.assertTrue(ok)
            self.assertEqual(vdb.count_chunks(), 3)

            # Replace with a 2-chunk version -> Old 3 chunks must be replaced atomically
            chunks_v2 = [
                (0, "Paragraph 1 v2", "sha4", [0.8, 0.2]),
                (1, "Paragraph 2 v2", "sha5", [0.2, 0.8]),
            ]
            ok2 = vdb.upsert_document_chunks(
                doc_id="DOC-ATOMIC",
                relative_path="docs/atomic.md",
                chunks=chunks_v2,
                provenance="real",
                model_name="local-embed",
            )
            self.assertTrue(ok2)
            self.assertEqual(vdb.count_chunks(), 2)

    def test_query_semantic_search_and_rag_synthesis(self):
        from unittest.mock import patch
        from tools.query import semantic_search_library, ask_library
        from tools.inference.local_client import LocalInferenceClient

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cat_dir = tmp_path / "catalog"
            cat_dir.mkdir(parents=True, exist_ok=True)
            db_file = cat_dir / "library_vectors.db"

            from tools.indexer.embed_corpus import LibraryVectorDB
            vdb = LibraryVectorDB(db_file)
            vdb.upsert_chunk(
                doc_id="ADR-048",
                relative_path="docs/adr/ADR-048.md",
                chunk_index=0,
                chunk_text="ADR-048 defines the Local Inference Substrate and Dual-Engine compute plane.",
                sha256="sha_adr48",
                embedding=[1.0, 0.0, 0.0],
                provenance="real",
                model_name="local-embed",
            )

            client = LocalInferenceClient()
            with patch.object(client, "health_check", return_value={"online": True}):
                with patch.object(client, "generate_embeddings", return_value=[[1.0, 0.0, 0.0]]):
                    results = semantic_search_library("local inference", max_results=3, client=client, root_dir=tmp_path)
                    self.assertTrue(len(results) > 0)
                    self.assertEqual(results[0].doc_id, "ADR-048")
                    self.assertGreater(results[0].score, 0.99)

                with patch.object(client, "generate_embeddings", return_value=[[1.0, 0.0, 0.0]]):
                    with patch.object(client, "chat_completion", return_value="ADR-048 is the local substrate specification."):
                        rag_res = ask_library("What is ADR-048?", max_context_chunks=2, client=client, root_dir=tmp_path)
                        self.assertIn("ADR-048 is the local substrate", rag_res["answer"])
                        self.assertEqual(rag_res["sources"], ["docs/adr/ADR-048.md"])

    def test_summarize_reference_pipeline(self):
        from unittest.mock import patch
        from tools.inference.summarize_reference import summarize_document
        from tools.inference.local_client import LocalInferenceClient

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            sample_file = tmp_path / "sample_paper.md"
            sample_file.write_text("# Deep Seek Architecture\nDetails on MoE routing and KV-cache compression.", encoding="utf-8")

            client = LocalInferenceClient()
            fake_summary_json = json.dumps({
                "title": "Deep Seek Architecture",
                "executive_summary": "Paper on Multi-head Latent Attention and MoE routing.",
                "key_findings": ["MLA reduces KV cache footprint", "Dynamic routing balances expert compute"],
                "matched_concepts": ["kv_cache", "mixture_of_experts"],
                "suggested_tags": ["mla", "moe", "efficiency"]
            })

            with patch.object(client, "chat_completion", return_value=fake_summary_json):
                summary = summarize_document(sample_file, client=client, ontology_concepts=["kv_cache", "moe"])
                self.assertEqual(summary["title"], "Deep Seek Architecture")
                self.assertEqual(len(summary["key_findings"]), 2)
                self.assertIn("kv_cache", summary["matched_concepts"])

    def test_translate_reference_pipeline(self):
        from unittest.mock import patch
        from tools.inference.translate_reference import translate_markdown
        from tools.inference.local_client import LocalInferenceClient

        client = LocalInferenceClient()
        fake_translation = "# Arquitetura de Inferência Local\nEste documento descreve o pipeline de execução."

        with patch.object(client, "chat_completion", return_value=fake_translation):
            res = translate_markdown("# Local Inference Architecture\nThis document describes the pipeline.", client=client)
            self.assertIn("Arquitetura de Inferência Local", res)

    def test_harvester_classification_and_crawler(self):
        from tools.bookkeeper.harvest_corpus import (
            classify_document_type,
            scan_source_directory,
            run_harvester,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            ext_source = tmp_path / "external_repo"
            ext_source.mkdir(parents=True, exist_ok=True)
            lib_root = tmp_path / "lib_repo"
            lib_root.mkdir(parents=True, exist_ok=True)

            # Create test documents in external source
            doc_adr = ext_source / "ADR-099_federated_harvesting.md"
            doc_adr.write_text("# ADR-099: Federated Harvesting\nSpecifications for multi-source crawler.", encoding="utf-8")

            doc_spec = ext_source / "SPEC-KERNEL-002.md"
            doc_spec.write_text("# SPEC-KERNEL-002: Kernel OpenSDD\nStrict execution envelope.", encoding="utf-8")

            doc_noise = ext_source / "package-lock.json"
            doc_noise.write_text("{}", encoding="utf-8")

            doc_tiny = ext_source / "stub.md"
            doc_tiny.write_text("abc", encoding="utf-8")  # < 100 bytes -> ignored

            # Classification checks
            self.assertEqual(classify_document_type(doc_adr, doc_adr.read_text("utf-8")), "adr")
            self.assertEqual(classify_document_type(doc_spec, doc_spec.read_text("utf-8")), "spec")

            # Scan source directory (Dry-Run mode)
            discovered = scan_source_directory(ext_source, library_root=lib_root)
            self.assertEqual(len(discovered), 2)  # ADR and SPEC; noise & stub ignored
            self.assertTrue(all(d.status == "NEW" for d in discovered))

            # Run harvester with apply=True
            report = run_harvester([ext_source], apply_ingest=True, library_root=lib_root)
            self.assertEqual(report.ingested_count, 2)

            # Re-running harvester must detect exact duplicates (idempotence)
            report_re = run_harvester([ext_source], apply_ingest=True, library_root=lib_root)
            self.assertEqual(report_re.ingested_count, 0)
            self.assertEqual(report_re.skipped_duplicate_count, 2)


if __name__ == "__main__":
    unittest.main()
