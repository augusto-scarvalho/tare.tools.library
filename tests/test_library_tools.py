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

    def test_ingest_duplicate_boundary_90_percent(self):
        from tools.ingest import compute_similarity
        # Build 10 shingles, 9 shared -> Jaccard = 9 / (10 + 10 - 9) = 9/11 = ~0.818
        # Build 20 shingles with 19 shared -> Jaccard = 19 / (20 + 20 - 19) = 19/21 = ~0.9047
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

    def test_atomic_manifest_publication(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            manifest = build_library_manifest(root_dir=tmp_path)
            out_file = save_manifest(manifest, root_dir=tmp_path)
            self.assertTrue(out_file.exists())
            # Ensure no residual .tmp files exist in catalog/
            tmp_files = list((tmp_path / "catalog").glob("*.tmp"))
            self.assertEqual(len(tmp_files), 0)

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
        client = LocalInferenceClient(LocalInferenceConfig(host="http://127.0.0.1:59999", timeout_seconds=1.0))
        res = client.readiness_check(require_cuda=True)
        self.assertFalse(res["ready"])
        self.assertIn("error", res)

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


if __name__ == "__main__":
    unittest.main()
