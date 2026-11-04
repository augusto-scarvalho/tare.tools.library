"""Unit tests for Incremental Content-Addressed Vector Indexing (ADR-058)."""

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.indexer.embed_corpus import LibraryVectorDB, index_corpus


class OfflineEmbeddingClient:
    def health_check(self, target="embed"):
        return {"online": False, "target": target}


class TestIncrementalIndexer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_vectors.db"
        self.db = LibraryVectorDB(self.db_path)
        self.client = OfflineEmbeddingClient()

        # Create 3 test markdown files
        self.doc1 = self.temp_dir / "doc1.md"
        self.doc2 = self.temp_dir / "doc2.md"
        self.doc3 = self.temp_dir / "doc3.md"

        self.doc1.write_text("# Doc 1\n\nFirst test document.", encoding="utf-8")
        self.doc2.write_text("# Doc 2\n\nSecond test document.", encoding="utf-8")
        self.doc3.write_text("# Doc 3\n\nThird test document.", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_first_index_processes_all_documents(self):
        """First run should vectorize all 3 documents."""
        indexed = index_corpus(self.temp_dir, client=self.client, db=self.db)
        self.assertGreater(indexed, 0)
        self.assertEqual(len(self.db.get_indexed_file_hashes()), 3)

    def test_second_index_skips_all_unchanged_documents(self):
        """Second run without modifications should compute 0 embeddings."""
        index_corpus(self.temp_dir, client=self.client, db=self.db)
        initial_count = self.db.count_chunks()

        # Run indexer again
        reindexed = index_corpus(self.temp_dir, client=self.client, db=self.db)
        self.assertEqual(reindexed, 0)
        self.assertEqual(self.db.count_chunks(), initial_count)

    def test_modifying_one_document_indexes_only_that_document(self):
        """Modifying 1 document should only re-index that single document."""
        index_corpus(self.temp_dir, client=self.client, db=self.db)

        # Modify doc2
        self.doc2.write_text("# Doc 2 Modified\n\nNew content with more information.", encoding="utf-8")

        reindexed = index_corpus(self.temp_dir, client=self.client, db=self.db)
        self.assertGreater(reindexed, 0)
        # Verify hashes mapping contains the updated hash
        hashes = self.db.get_indexed_file_hashes()
        self.assertIn("doc2.md", hashes)

    def test_deleting_document_purges_orphaned_chunks(self):
        """Deleting a document from disk purges its vectors from the database."""
        index_corpus(self.temp_dir, client=self.client, db=self.db)
        self.assertIn("doc3.md", self.db.get_indexed_file_hashes())

        # Delete doc3
        self.doc3.unlink()

        # Run indexer again
        index_corpus(self.temp_dir, client=self.client, db=self.db)
        self.assertNotIn("doc3.md", self.db.get_indexed_file_hashes())

    def test_force_reindex_all_bypasses_cache(self):
        """Passing force_reindex=True re-vectorizes everything regardless of hash."""
        index_corpus(self.temp_dir, client=self.client, db=self.db)

        # Force reindex
        reindexed = index_corpus(
            self.temp_dir, client=self.client, db=self.db, force_reindex=True
        )
        self.assertGreater(reindexed, 0)

    def test_default_scope_excludes_history_and_exact_duplicates(self):
        active = self.temp_dir / "docs" / "research" / "active.md"
        duplicate = self.temp_dir / "docs" / "research" / "active_deadbeef.md"
        history = self.temp_dir / "docs" / "archive" / "old.md"
        snapshot = self.temp_dir / "catalog" / "corpus" / "snapshot.md"
        projection = self.temp_dir / "catalog" / "frontier" / "pointer.md"
        for path in (active, duplicate, history, snapshot, projection):
            path.parent.mkdir(parents=True, exist_ok=True)
        active.write_text("# Active\n\nUnique active payload.", encoding="utf-8")
        duplicate.write_bytes(active.read_bytes())
        history.write_text("# Historical\n\nArchive payload.", encoding="utf-8")
        snapshot.write_text("# Snapshot\n\nSnapshot payload.", encoding="utf-8")
        projection.write_text("# Projection\n\nGenerated projection.", encoding="utf-8")

        index_corpus(self.temp_dir, client=self.client, db=self.db)
        indexed = self.db.get_indexed_file_hashes()
        self.assertIn("docs/research/active.md", indexed)
        self.assertNotIn("docs/research/active_deadbeef.md", indexed)
        self.assertNotIn("docs/archive/old.md", indexed)
        self.assertNotIn("catalog/corpus/snapshot.md", indexed)
        self.assertNotIn("catalog/frontier/pointer.md", indexed)

        index_corpus(
            self.temp_dir, client=self.client, db=self.db, include_history=True
        )
        indexed_with_history = self.db.get_indexed_file_hashes()
        self.assertIn("docs/archive/old.md", indexed_with_history)
        self.assertIn("catalog/corpus/snapshot.md", indexed_with_history)
        self.assertNotIn("catalog/frontier/pointer.md", indexed_with_history)


if __name__ == "__main__":
    unittest.main()


class FakeOnlineClient:
    """Deterministic 4-dim vectors so owner rows land as real vectors without a server."""

    def health_check(self, target="embed"):
        return {"online": True, "target": target}

    def generate_embeddings(self, texts, *, is_query=False):
        return [[float(len(t) % 7), 1.0, 0.0, 0.5] for t in texts]


class TestOwnerRootIndexing(unittest.TestCase):
    """Owner documents are read where they live and indexed as `repository:path`."""

    ADR = "tare.tools.os:docs/adr/ADR-062_FRUGAL.md"

    def git(self, *args):
        import subprocess

        subprocess.run(["git", "-C", str(self.owner), "-c", "user.email=t@x", "-c", "user.name=t", *args],
                       check=True, capture_output=True)

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.library = self.temp_dir / "tare.tools.library"
        (self.library / "docs").mkdir(parents=True)
        (self.library / "docs" / "local.md").write_text("# Local\n\nLibrary document.", encoding="utf-8")
        self.owner = self.temp_dir / "tare.tools.os"
        for name, text in {
            "docs/adr/ADR-062_FRUGAL.md": "# ADR-062: Frugal doctrine\n\nADR text in the owner repository.\n",
            "docs/archive/old.md": "# Old\n\nHistory stays opt-in.\n",
            "ontology/domain_ontology.yaml": "concepts:\n  - id: FrugalDoctrine\n    name: Frugal doctrine\n"
                                             "    governing_adr: ADR-062\n",
        }.items():
            (self.owner / name).parent.mkdir(parents=True, exist_ok=True)
            (self.owner / name).write_text(text, encoding="utf-8")
        self.git("init", "-q")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        (self.owner / "untracked.md").write_text("# Untracked\n", encoding="utf-8")
        self.db = LibraryVectorDB(self.library / "catalog" / "test_vectors.db")
        self.owner_roots = {"tare.tools.os": self.owner}

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def index(self, owner_roots=None):
        return index_corpus(self.library, client=FakeOnlineClient(), db=self.db, owner_roots=owner_roots)

    def test_tracked_owner_markdown_is_indexed_and_anchored_where_it_lives(self):
        import sqlite3

        self.assertGreater(self.index(self.owner_roots), 0)
        self.assertEqual(set(self.db.get_indexed_file_hashes()), {"docs/local.md", self.ADR})
        with sqlite3.connect(self.db.db_path) as conn:
            concepts = conn.execute("SELECT DISTINCT concepts FROM document_chunks WHERE relative_path = ?",
                                    (self.ADR,)).fetchall()
        self.assertEqual(concepts, [('["FrugalDoctrine"]',)])
        self.assertEqual(self.index(self.owner_roots), 0)  # unchanged rerun embeds nothing

    def test_a_run_removes_stale_rows_only_for_the_roots_it_read(self):
        self.index(self.owner_roots)
        other = "tare.tools.kernel:docs/spec.md"
        legacy = "tare.tools.os@" + "a" * 40 + ":docs/adr/ADR-062_FRUGAL.md"  # a row of the deleted catalog
        for identity in (other, legacy):
            self.db.upsert_document_chunks("doc", identity, [(0, "body", "sha", [1.0, 0.0, 0.0, 0.0])])
        self.index()  # no owner roots: owner rows stay, the legacy row goes
        self.assertEqual(set(self.db.get_indexed_file_hashes()), {"docs/local.md", self.ADR, other})
        self.git("rm", "-q", "docs/adr/ADR-062_FRUGAL.md")
        self.git("commit", "-qm", "drop")
        self.index(self.owner_roots)
        self.assertEqual(set(self.db.get_indexed_file_hashes()), {"docs/local.md", other})

    def test_unavailable_owner_refuses_the_run_and_keeps_its_rows(self):
        self.index(self.owner_roots)
        before = self.db.get_indexed_file_hashes()
        with self.assertRaisesRegex(ValueError, "Owner checkout unavailable: tare.tools.os"):
            self.index({"tare.tools.os": self.temp_dir / "missing"})
        self.assertEqual(self.db.get_indexed_file_hashes(), before)


class TestOntologyEnrichment(unittest.TestCase):
    CONCEPTS = [
        {"id": "TripartiteRoundTable", "name": "Independent Multi-Seat Deliberation", "governing_adr": "ADR-047",
         "domain": "Deliberation & Architectural Governance", "relationships": {"governs": ["ArchitecturalDeliberation"]}},
        {"id": "CasLeasedGraphMutation", "name": "CAS leased graph mutation", "governing_adr": "ADR-030"},
    ]

    def test_anchoring_by_governing_adr_id_and_name(self):
        from tools.indexer.embed_corpus import anchor_concepts
        by_adr = anchor_concepts("text without a mention", "tare.tools.os:docs/adr/ADR-047_X.md", self.CONCEPTS)
        self.assertEqual([c["id"] for c in by_adr], ["TripartiteRoundTable"])
        by_id = anchor_concepts("uses CasLeasedGraphMutation in the landing", "doc", self.CONCEPTS)
        self.assertEqual([c["id"] for c in by_id], ["CasLeasedGraphMutation"])
        by_name = anchor_concepts("an independent multi-seat deliberation happens", "doc", self.CONCEPTS)
        self.assertEqual([c["id"] for c in by_name], ["TripartiteRoundTable"])
        self.assertEqual(anchor_concepts("CasLeasedGraphMutations plural does not match", "doc", self.CONCEPTS), [])

    def test_governing_adr_anchors_only_inside_the_owner_repository(self):
        from tools.indexer.embed_corpus import anchor_concepts, document_repository
        concepts = [{"id": "CASPersistence", "name": "CAS", "governing_adr": "ADR-001", "repository": "tare.tools.kernel"},
                    {"id": "SpelGuard", "name": "SpEL", "governing_adr": "ADR-0007", "repository": "tare.tools.dialog-engine"}]
        # Every satellite has an ADR-001: the SpecGraph north star must not inherit Kernel concepts
        self.assertEqual(anchor_concepts("x", "ADR-001_SPECGRAPH_NORTH_STAR", concepts, repository="tare.tools.specgraph"), [])
        self.assertEqual([c["id"] for c in anchor_concepts("x", "ADR-001_KERNEL", concepts, repository="tare.tools.kernel")],
                         ["CASPersistence"])
        # Zero-padded ids (ADR-0007 vs 0007-...) name the same decision
        self.assertEqual([c["id"] for c in anchor_concepts("x", "tare.tools.dialog-engine:docs/adr/0007-dialog-engine-north-star.md", concepts,
                                                            repository="tare.tools.dialog-engine")], ["SpelGuard"])
        # A spec anchors its owner's concepts by id in the document id or in its header block, never by a
        # cross-reference deep in the body, and never across owners
        specs = [{"id": "CASPersistence", "name": "CAS", "governing_spec": "SPEC-KERNEL-001", "repository": "tare.tools.kernel"}]
        self.assertEqual([c["id"] for c in anchor_concepts("x", "tare.tools.kernel:docs/SPEC-KERNEL-001.md", specs,
                                                            repository="tare.tools.kernel")], ["CASPersistence"])
        self.assertEqual([c["id"] for c in anchor_concepts("Status: SPEC-KERNEL-001 v1", "spec.md", specs,
                                                            repository="tare.tools.kernel")], ["CASPersistence"])
        self.assertEqual(anchor_concepts("SPEC-KERNEL-0012 is not the same", "spec.md", specs, repository="tare.tools.kernel"), [])
        self.assertEqual(anchor_concepts("y" * 700 + "SPEC-KERNEL-001", "spec.md", specs, repository="tare.tools.kernel"), [])
        self.assertEqual(anchor_concepts("x", "tare.tools.os:docs/SPEC-KERNEL-001.md", specs, repository="tare.tools.os"), [])
        self.assertEqual(document_repository("tare.tools.os:docs/adr/ADR-055.md"), "tare.tools.os")
        self.assertEqual(document_repository("docs/ADR-069.md"), "tare.tools.library")

    def test_chunk_header_carries_identity_triples_and_heading_path(self):
        from tools.indexer.embed_corpus import chunk_markdown, concept_header, document_header
        content = "# ADR-047: Table" + chr(10) * 2 + "Intro." + chr(10) * 2 + "## Decision" + chr(10) * 2 + "Decision body."
        header = " | ".join([document_header("ADR-047", "docs/adr/ADR-047.md", content), concept_header(self.CONCEPTS[:1])])
        chunks = chunk_markdown(content, header=header)
        self.assertEqual(len(chunks), 1)
        first = chunks[0].splitlines()[0]
        self.assertIn("[adr] ADR-047 | ADR-047: Table", first)
        self.assertIn("concepts: TripartiteRoundTable (Independent Multi-Seat Deliberation; domain: Deliberation", first)
        self.assertIn("governs: ArchitecturalDeliberation", first)
        self.assertTrue(first.endswith("ADR-047: Table > Decision"))

    def test_old_schema_is_migrated_so_two_namespaces_coexist(self):
        import sqlite3

        temp = Path(tempfile.mkdtemp())
        try:
            db_path = temp / "old.db"
            conn = sqlite3.connect(db_path)
            conn.execute("""CREATE TABLE document_chunks (id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL,
                relative_path TEXT NOT NULL, chunk_index INTEGER NOT NULL, chunk_text TEXT NOT NULL, sha256 TEXT NOT NULL,
                dimensions INTEGER NOT NULL DEFAULT 32, provenance TEXT NOT NULL DEFAULT 'real',
                model_name TEXT NOT NULL DEFAULT 'local-embed', embedding_json TEXT NOT NULL, UNIQUE(relative_path, chunk_index))""")
            conn.execute("INSERT INTO document_chunks (doc_id, relative_path, chunk_index, chunk_text, sha256, dimensions, provenance, model_name, embedding_json) VALUES ('d','a.md',0,'t','s',2,'real','local-embed','[1,0]')")
            conn.commit(); conn.close()
            db = LibraryVectorDB(db_path)
            self.assertTrue(db.upsert_document_chunks("d", "a.md", [(0, "t", "s2", [0.0, 1.0])], model_name="qwen3-embedding-4b", concepts=["X"]))
            conn = sqlite3.connect(db_path)
            rows = conn.execute("SELECT model_name, concepts FROM document_chunks WHERE relative_path='a.md' ORDER BY model_name").fetchall()
            conn.close()
            self.assertEqual(rows, [("local-embed", "[]"), ("qwen3-embedding-4b", '["X"]')])
        finally:
            shutil.rmtree(temp, ignore_errors=True)
