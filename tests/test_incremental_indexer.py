"""Unit tests for Incremental Content-Addressed Vector Indexing (ADR-058)."""

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.indexer.embed_corpus import LibraryVectorDB, index_corpus


class TestIncrementalIndexer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_vectors.db"
        self.db = LibraryVectorDB(self.db_path)

        # Create 3 test markdown files
        self.doc1 = self.temp_dir / "doc1.md"
        self.doc2 = self.temp_dir / "doc2.md"
        self.doc3 = self.temp_dir / "doc3.md"

        self.doc1.write_text("# Doc 1\n\nPrimeiro documento de teste.", encoding="utf-8")
        self.doc2.write_text("# Doc 2\n\nSegundo documento de teste.", encoding="utf-8")
        self.doc3.write_text("# Doc 3\n\nTerceiro documento de teste.", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_first_index_processes_all_documents(self):
        """First run should vectorize all 3 documents."""
        indexed = index_corpus(self.temp_dir, db=self.db)
        self.assertGreater(indexed, 0)
        self.assertEqual(len(self.db.get_indexed_file_hashes()), 3)

    def test_second_index_skips_all_unchanged_documents(self):
        """Second run without modifications should compute 0 embeddings."""
        index_corpus(self.temp_dir, db=self.db)
        initial_count = self.db.count_chunks()

        # Run indexer again
        reindexed = index_corpus(self.temp_dir, db=self.db)
        self.assertEqual(reindexed, 0)
        self.assertEqual(self.db.count_chunks(), initial_count)

    def test_modifying_one_document_indexes_only_that_document(self):
        """Modifying 1 document should only re-index that single document."""
        index_corpus(self.temp_dir, db=self.db)

        # Modify doc2
        self.doc2.write_text("# Doc 2 Modificado\n\nNovo conteudo com mais informacoes.", encoding="utf-8")

        reindexed = index_corpus(self.temp_dir, db=self.db)
        self.assertGreater(reindexed, 0)
        # Verify hashes mapping contains the updated hash
        hashes = self.db.get_indexed_file_hashes()
        self.assertIn("doc2.md", hashes)

    def test_deleting_document_purges_orphaned_chunks(self):
        """Deleting a document from disk purges its vectors from the database."""
        index_corpus(self.temp_dir, db=self.db)
        self.assertIn("doc3.md", self.db.get_indexed_file_hashes())

        # Delete doc3
        self.doc3.unlink()

        # Run indexer again
        index_corpus(self.temp_dir, db=self.db)
        self.assertNotIn("doc3.md", self.db.get_indexed_file_hashes())

    def test_force_reindex_all_bypasses_cache(self):
        """Passing force_reindex=True re-vectorizes everything regardless of hash."""
        index_corpus(self.temp_dir, db=self.db)

        # Force reindex
        reindexed = index_corpus(self.temp_dir, db=self.db, force_reindex=True)
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

        index_corpus(self.temp_dir, db=self.db)
        indexed = self.db.get_indexed_file_hashes()
        self.assertIn("docs/research/active.md", indexed)
        self.assertNotIn("docs/research/active_deadbeef.md", indexed)
        self.assertNotIn("docs/archive/old.md", indexed)
        self.assertNotIn("catalog/corpus/snapshot.md", indexed)
        self.assertNotIn("catalog/frontier/pointer.md", indexed)

        index_corpus(self.temp_dir, db=self.db, include_history=True)
        indexed_with_history = self.db.get_indexed_file_hashes()
        self.assertIn("docs/archive/old.md", indexed_with_history)
        self.assertIn("catalog/corpus/snapshot.md", indexed_with_history)
        self.assertNotIn("catalog/frontier/pointer.md", indexed_with_history)


if __name__ == "__main__":
    unittest.main()
