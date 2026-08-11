import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'refresh-editions'/'2026-08-11'
class RefreshTests(unittest.TestCase):
    def test_refresh_coverage_and_qa(self):
        qa=json.loads((REF/'REFRESH_QA.json').read_text(encoding='utf-8'))
        self.assertEqual(qa['status'],'PASS')
        self.assertEqual(qa['html_files'],22)
        self.assertEqual(qa['lineage_html_files'],20)
        self.assertEqual(qa['supplemental_html_files'],2)
        self.assertEqual(qa['scientific_lineages'],9)
        self.assertEqual(qa['historical_crosswalk_rows'],93)
        self.assertEqual(qa['broken_navigation_links'],[])
        self.assertEqual(qa['errors'],[])
    def test_refresh_source_index(self):
        d=json.loads((REF/'REFRESH_SOURCE_INDEX.json').read_text(encoding='utf-8'))
        self.assertEqual(d['html_documents'],22)
        self.assertGreaterEqual(d['unique_external_urls'],50)
    def test_refresh_navigation_artifacts(self):
        for name in ['README.md','REFRESH_CROSSWALK.md','CORPUS_CURATION_MAP.md','REFRESH_MANIFEST.json','RESEARCH_DOCUMENT_STANDARD.md']:
            self.assertTrue((REF/name).is_file(),name)
if __name__=='__main__': unittest.main()
