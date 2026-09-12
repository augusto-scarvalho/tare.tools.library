"""Behavioral regressions for document identity and retrieval provenance."""
import contextlib, io, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch, Mock
from tools import query as q

class ExactIdentity(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'docs/adr').mkdir(parents=True)
        (self.root / 'specs').mkdir()

    def put(self, path, text):
        (self.root / path).write_text(text, encoding='utf-8')

    def test_adr_prefix_collision_is_absent(self):
        self.put('docs/adr/ADR-0010_Long.md', 'wrong')
        self.assertIsNone(q.get_adr('ADR-001', self.root))

    def test_spec_prefix_collision_is_absent(self):
        self.put('specs/SPEC-LIBRARY-0010_Long.md', 'wrong')
        self.assertIsNone(q.get_spec('SPEC-LIBRARY-001', self.root))

    def test_nonleading_identifier_is_absent(self):
        self.put('docs/adr/NOTE-ADR-001.md', 'wrong')
        self.put('specs/NOTE-SPEC-LIBRARY-001.md', 'wrong')
        self.assertIsNone(q.get_adr('ADR-001', self.root))
        self.assertIsNone(q.get_spec('SPEC-LIBRARY-001', self.root))

    def test_empty_identity_is_absent(self):
        self.put('docs/adr/ADR-000.md', 'wrong')
        self.put('specs/SPEC-LIBRARY-001.md', 'wrong')
        for value in ['', '  ']:
            self.assertIsNone(q.get_adr(value, self.root))
            self.assertIsNone(q.get_spec(value, self.root))

    def test_compatible_identifiers(self):
        self.put('docs/adr/ADR-051_Federation.md', 'expected ADR')
        self.put('specs/SPEC-LIBRARY-001.md', 'expected SPEC')
        for value in ['051', '51', ' adr-051 ']:
            self.assertEqual(q.get_adr(value, self.root), 'expected ADR')
        self.assertEqual(q.get_spec(' spec-library-001 ', self.root), 'expected SPEC')
        (self.root / 'specs/SPEC-LIBRARY-001.md').unlink()
        self.put('specs/SPEC-LIBRARY-001_Title.md', 'titled SPEC')
        self.assertEqual(q.get_spec('SPEC-LIBRARY-001', self.root), 'titled SPEC')

class FallbackProvenance(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'docs').mkdir()
        (self.root / 'docs/alpha.md').write_text('# Alpha\n\nneedle needle needle\n', encoding='utf-8')

    def test_absent_index_tags_and_preserves_lexical_results(self):
        lexical = q.search_library('needle', root_dir=self.root)
        self.assertTrue(lexical)
        client = Mock()
        client.health_check.side_effect = AssertionError('No endpoint call without an index')
        with patch('tools.indexer.embed_corpus.LibraryVectorDB', side_effect=AssertionError('No database construction without an index')):
            result = q.semantic_search_library('needle', client=client, root_dir=self.root)
        self.assertEqual([r.doc_type for r in result], ['lexical_fallback'] * len(lexical))
        for a, b in zip(result, lexical):
            for key in ['doc_id', 'title', 'relative_path', 'snippet', 'score']:
                self.assertEqual(getattr(a, key), getattr(b, key))
        client.health_check.assert_not_called()

    def test_cli_never_labels_keyword_count_as_cosine(self):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['query', '--semantic', 'needle', '--force-local', '--root', str(self.root)]), contextlib.redirect_stdout(output):
            self.assertEqual(q.main(), 0)
        text = output.getvalue()
        self.assertIn('FALLBACK', text)
        self.assertIn('Term Matches', text)
        self.assertNotIn('Cosine', text)
        self.assertNotIn('Endpoint Offline', text)

    def test_empty_results_and_limit_preserved(self):
        self.assertEqual(q.semantic_search_library('missing', root_dir=self.root), [])
        self.assertEqual(q.semantic_search_library('needle', max_results=0, root_dir=self.root), [])

    def test_live_vector_results_remain_semantic(self):
        (self.root / 'catalog').mkdir()
        (self.root / 'catalog/library_vectors.db').touch()
        row = Mock(doc_id='vector-id', relative_path='docs/vector.md', text_snippet='vector', score=0.75)
        client = Mock()
        client.health_check.return_value = {'online': True}
        client.generate_embeddings.return_value = [[1.0]]
        with patch('tools.indexer.embed_corpus.LibraryVectorDB') as db:
            db.return_value.search.return_value = [row]
            result = q.semantic_search_library('needle', client=client, root_dir=self.root)
        self.assertEqual(result[0].doc_type, 'vector_semantic')
        self.assertEqual(result[0].score, 0.75)
