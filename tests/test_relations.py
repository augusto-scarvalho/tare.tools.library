import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'catalog'
class RelationGraphTests(unittest.TestCase):
    def test_graph_integrity(self):
        g=json.loads((CAT/'RESEARCH_RELATION_GRAPH.json').read_text(encoding='utf-8'))
        ids=[n['id'] for n in g['nodes']]
        self.assertEqual(len(ids),len(set(ids)))
        known=set(ids)
        self.assertEqual(g['statistics']['historical_artifacts'],93)
        self.assertEqual(g['statistics']['refresh_documents'],20)
        self.assertGreaterEqual(g['statistics']['external_sources'],50)
        self.assertGreaterEqual(g['statistics']['curated_cross_lineage_edges'],20)
        for e in g['edges']:
            self.assertIn(e['from'],known)
            self.assertIn(e['to'],known)
            self.assertIn(e['confidence'],{'high','medium','low'})
    def test_relationship_docs_exist(self):
        for name in ['RESEARCH_LINEAGE_AND_INFLUENCE.md','RESEARCH_LINEAGE_AND_INFLUENCE.html','RESEARCH_RELATIONSHIP_STANDARD.md','DOCUMENT_RELATIONSHIP_ADDITION_PROPOSAL.md','SOURCE_FAMILIES.md','SOURCE_CO_CITATION.md','SOURCE_IDENTITY_REVIEW_QUEUE.md']:
            self.assertTrue((CAT/name).is_file(),name)
if __name__=='__main__': unittest.main()
