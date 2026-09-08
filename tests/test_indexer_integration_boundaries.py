"""Offline falsifiers for the pending federated indexer integration."""
import json
import sqlite3
import subprocess
import sys
from unittest.mock import patch

import pytest

from tools.indexer.embed_corpus import LibraryVectorDB, _bounded_paragraphs, index_corpus
from tools.inference.local_client import LocalInferenceClient, LocalInferenceConfig


class ShortResponseClient:
    def health_check(self, target='embed'):
        return {'online': True}

    def generate_embeddings(self, texts, **kwargs):
        return []


def test_short_embedding_response_preserves_complete_upgradeable_document(tmp_path):
    (tmp_path / 'doc.md').write_text('# Example\n\nBody.', encoding='utf-8')
    db = LibraryVectorDB(tmp_path / 'vectors.db')
    assert index_corpus(tmp_path, client=ShortResponseClient(), db=db) > 0
    with sqlite3.connect(db.db_path) as connection:
        rows = connection.execute('SELECT provenance, chunk_text FROM document_chunks').fetchall()
    assert rows and all(provenance == 'pseudo' for provenance, _ in rows)
    assert 'Body.' in rows[0][1]
    assert db.get_indexed_file_hashes(include_pseudo=False) == {}


def test_failed_transaction_is_not_counted_as_indexed(tmp_path):
    (tmp_path / 'doc.md').write_text('# Example\n\nBody.', encoding='utf-8')
    db = LibraryVectorDB(tmp_path / 'vectors.db')
    with patch.object(db, 'upsert_document_chunks', return_value=False):
        assert index_corpus(tmp_path, client=ShortResponseClient(), db=db) == 0
    assert db.count_chunks() == 0


def test_unavailable_selected_owner_cannot_purge_existing_federated_rows(tmp_path):
    (tmp_path / 'catalog').mkdir()
    registry = {'schema': 'tare.tools/federated-document-index/1.0',
        'source_library': {'repository': 'tare.tools.library', 'revision': '0' * 40},
        'retired_library_path_count': 0, 'local_retirements': [],
        'repositories': [{'repository': 'owner', 'revision': 'a' * 40, 'documents': [{
            'semantic_document_id': 'owner:docs/spec.md', 'document_type': 'spec',
            'title': 'SPEC', 'canonical_path': 'docs/spec.md', 'canonical_sha256': 'b' * 64,
            'migration': 'owner-origin', 'retired_library_paths': []}]}]}
    (tmp_path / 'catalog/FEDERATED_DOCUMENTS.json').write_text(json.dumps(registry))
    db = LibraryVectorDB(tmp_path / 'vectors.db')
    identity = 'owner@' + 'a' * 40 + ':docs/spec.md'
    db.upsert_document_chunks('spec', identity, [(0, 'body', 'b' * 64, [1.0])])
    with pytest.raises(ValueError, match='Explicit document checkout unavailable'):
        index_corpus(tmp_path, client=ShortResponseClient(), db=db, owner_roots={})
    assert identity in db.get_indexed_file_hashes()


def test_long_line_after_short_prefix_respects_paragraph_bound():
    parts = _bounded_paragraphs(['prefix\n' + 'x' * 2600])
    assert all(len(part) <= 1200 for part in parts)
    assert ''.join(parts) == 'prefix\n' + 'x' * 2600


def test_federated_cli_requires_explicit_owner_before_network_or_index(tmp_path):
    result = subprocess.run([sys.executable, '-m', 'tools.indexer.embed_corpus',
                             '--root', str(tmp_path), '--federated'], capture_output=True, text=True)
    assert result.returncode == 2
    assert 'requires explicit --owner-root' in result.stderr
    assert not (tmp_path / 'catalog').exists()


def test_namespace_migration_preserves_previous_rows(tmp_path):
    path = tmp_path / 'legacy.db'
    with sqlite3.connect(path) as connection:
        connection.execute('CREATE TABLE document_chunks (id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL, '
            'relative_path TEXT NOT NULL, chunk_index INTEGER NOT NULL, chunk_text TEXT NOT NULL, sha256 TEXT NOT NULL, '
            'dimensions INTEGER NOT NULL DEFAULT 32, provenance TEXT NOT NULL DEFAULT \'real\', '
            'model_name TEXT NOT NULL DEFAULT \'local-embed\', embedding_json TEXT NOT NULL, UNIQUE(relative_path, chunk_index))')
        connection.execute("INSERT INTO document_chunks(doc_id, relative_path, chunk_index, chunk_text, sha256, dimensions, model_name, embedding_json) VALUES('doc','doc.md',0,'old','hash',1,'old-model','[1.0]')")
    db = LibraryVectorDB(path)
    assert db.upsert_document_chunks('doc', 'doc.md', [(0, 'new', 'hash2', [2.0])], model_name='new-model')
    with sqlite3.connect(path) as connection:
        assert connection.execute('SELECT model_name, chunk_text FROM document_chunks ORDER BY model_name').fetchall() == [('new-model', 'new'), ('old-model', 'old')]


def test_embedding_batch_restores_order_and_never_fabricates_failed_vectors():
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self):
            return json.dumps({'data': [{'index': 1, 'embedding': [2.0]}, {'index': 0, 'embedding': [1.0]}]}).encode()
    client = LocalInferenceClient(LocalInferenceConfig())
    with patch('urllib.request.urlopen', return_value=Response()):
        assert client.generate_embeddings(['first', '', 'second']) == [[1.0], None, [2.0]]
    with patch('urllib.request.urlopen', side_effect=OSError('offline')):
        assert client.generate_embeddings(['first', 'second']) == [None, None]
