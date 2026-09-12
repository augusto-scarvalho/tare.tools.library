"""Small corpus regressions; no endpoint, GPU or production index needed."""
import json
import sqlite3
import sys
from types import SimpleNamespace

import pytest

from tools import query
from tools.document_scope import collect_indexable_markdown, indexed_relative_paths
from tools.indexer.embed_corpus import DEFAULT_NAMESPACE, LibraryVectorDB, index_corpus


def put(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


def test_markdown_case_scope_and_dedup_are_portable(tmp_path):
    active = {'docs/one.md', 'docs/two.MD', 'docs/três.Md'}
    for name in active:
        put(tmp_path, name, 'needle ' + name)
    put(tmp_path, 'docs/duplicate.MD', 'needle docs/one.md')
    history = {'docs/archive/old.MD', 'catalog/corpus/old.Md'}
    for name in history | {'catalog/generated.MD', 'docs/archive/not-markdown.txt'}:
        put(tmp_path, name, 'needle ' + name)
    assert set(indexed_relative_paths(tmp_path)) == active
    assert {r.relative_path for r in query.search_library('needle', root_dir=tmp_path)} == active
    assert set(indexed_relative_paths(tmp_path, include_history=True)) == active | history
    assert len(collect_indexable_markdown(tmp_path, deduplicate=False)) == 4


def test_incremental_index_retains_and_refreshes_uppercase_documents(tmp_path):
    offline = SimpleNamespace(health_check=lambda **kw: {'online': False})
    path = put(tmp_path, 'docs/upper.MD', '# Upper\n\nFirst content')
    put(tmp_path, 'docs/other.Md', '# Other\n\nDifferent content')
    db = LibraryVectorDB(tmp_path / 'catalog/library_vectors.db')
    assert index_corpus(tmp_path, client=offline, db=db) > 0
    before = db.get_indexed_file_hashes()
    assert set(before) == {'docs/upper.MD', 'docs/other.Md'}
    assert index_corpus(tmp_path, client=offline, db=db) == 0
    path.write_text('# Upper\n\nChanged content', encoding='utf-8')
    assert index_corpus(tmp_path, client=offline, db=db) > 0
    after = db.get_indexed_file_hashes()
    assert after['docs/upper.MD'] != before['docs/upper.MD']
    assert after['docs/other.Md'] == before['docs/other.Md']
    path.unlink()
    index_corpus(tmp_path, client=offline, db=db)
    assert set(db.get_indexed_file_hashes()) == {'docs/other.Md'}


class Client:
    config = SimpleNamespace(embedding_model=DEFAULT_NAMESPACE)
    messages = None
    def health_check(self, **kw):
        return {'online': True}
    def generate_embeddings(self, texts, **kw):
        return [[1.0, 0.0] for _ in texts]
    def chat_completion(self, messages, **kw):
        self.messages = messages
        return 'Offline test response'


@pytest.fixture
def mixed(tmp_path):
    db = LibraryVectorDB(tmp_path / 'catalog/library_vectors.db')
    active = 'docs/current.MD'
    canonical = 'example/owner@' + 'a' * 40 + ':architecture/decision.md'
    put(tmp_path, active, '# Active\n\nneedle current')
    for name, vector in [(active, [0.8, 0.6]), (canonical, [0.7, 0.7])]:
        db.upsert_chunk(name, name, 0, 'needle active', name, vector)
    for prefix in ('docs/archive', 'catalog/corpus', 'catalog/generated', 'tools'):
        for i in range(12):
            name = f'{prefix}/{i}.md'
            db.upsert_chunk(name, name, 0, 'FORBIDDEN_HISTORY needle', name, [1.0, 0.0])
    return tmp_path, db, Client(), [active, canonical]


def snapshot(db):
    with sqlite3.connect(db.db_path) as conn:
        return conn.execute('SELECT * FROM document_chunks ORDER BY id').fetchall()


def test_filter_precedes_ranking_limit_and_preserves_database(mixed):
    root, db, client, allowed = mixed
    before = snapshot(db)
    assert [r.relative_path for r in db.search([1, 0], top_k=2)] == allowed
    rows = query.semantic_search_library('needle', max_results=2, client=client, root_dir=root)
    assert [r.relative_path for r in rows] == allowed
    assert all(r.doc_type == 'vector_semantic' for r in rows)
    assert rows[0].score > rows[1].score
    assert snapshot(db) == before


def test_rag_context_and_sources_exclude_history(mixed):
    root, db, client, allowed = mixed
    result = query.ask_library('needle', max_context_chunks=2, client=client, root_dir=root)
    assert result['sources'] == allowed
    assert 'FORBIDDEN_HISTORY' not in json.dumps(client.messages)


@pytest.mark.parametrize('namespace', [DEFAULT_NAMESPACE, 'legacy-model'])
def test_no_admissible_vectors_preserves_lexical_fallback(tmp_path, namespace):
    db = LibraryVectorDB(tmp_path / 'catalog/library_vectors.db')
    put(tmp_path, 'docs/current.md', 'needle active')
    db.upsert_chunk('old', 'docs/archive/old.md', 0, 'forbidden needle', 'sha', [1, 0], model_name=namespace)
    rows = query.semantic_search_library('needle', client=Client(), root_dir=tmp_path)
    assert [(r.relative_path, r.doc_type) for r in rows] == [('docs/current.md', 'lexical_fallback')]
    assert db.count_chunks() == 1


def test_history_opt_in_does_not_admit_generated_catalogs(mixed):
    root, db, client, allowed = mixed
    rows = db.search([1, 0], top_k=100, include_history=True)
    assert len(rows) == 26  # 24 historical chunks plus two active references.
    assert all(not r.relative_path.startswith(('catalog/generated/', 'tools/')) for r in rows)
    assert set(allowed) <= {r.relative_path for r in rows}


def test_excluded_rows_are_not_scored_or_decoded(mixed):
    _, db, _, allowed = mixed
    with sqlite3.connect(db.db_path) as conn:
        conn.execute("UPDATE document_chunks SET embedding_json='invalid' WHERE relative_path LIKE 'docs/archive/%'")
    assert [r.relative_path for r in db.search([1, 0], top_k=2)] == allowed


@pytest.mark.parametrize('path', ['../docs/a.md', '/docs/a.md', 'C:\\docs\\a.md',
    'docs/../catalog/generated/a.md', 'docs/archive/a.md', 'catalog/generated/a.md',
    'docs/.git/a.md', 'owner@bad:docs/a.md', 'owner@' + 'a'*40 + ':docs/archive/a.md',
    'owner@' + 'a'*40 + ':catalog/generated/a.md'])
def test_vector_scope_rejects_history_generated_and_noncanonical_paths(tmp_path, path):
    db = LibraryVectorDB(tmp_path / 'vectors.db')
    db.upsert_chunk('invalid', path, 0, 'excluded', 'sha', [1, 0])
    assert db.search([1, 0]) == []


@pytest.mark.parametrize('history', [False, True])
def test_existing_vector_query_cli_keeps_explicit_history_choice(tmp_path, monkeypatch, capsys, history):
    from tools.indexer import embed_corpus as indexer
    db = LibraryVectorDB(tmp_path / 'catalog/library_vectors.db')
    for path in ('docs/current.md', 'docs/archive/old.md', 'catalog/generated.md'):
        db.upsert_chunk(path, path, 0, 'content', 'sha', [1.0]*32, provenance='pseudo')
    monkeypatch.setattr(indexer, 'LocalInferenceClient', lambda: SimpleNamespace(health_check=lambda **kw: {'online': False}))
    monkeypatch.setattr(sys, 'argv', ['embed_corpus', '--query', 'needle', '--root', str(tmp_path),
                                     *(['--include-history'] if history else [])])
    assert indexer.main() == 0
    output = capsys.readouterr().out
    assert 'docs/current.md' in output
    assert ('docs/archive/old.md' in output) == history
    assert 'catalog/generated.md' not in output
