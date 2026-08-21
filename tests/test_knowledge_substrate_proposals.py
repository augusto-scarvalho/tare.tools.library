import json, unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
class P(HTMLParser):
    def __init__(self): super().__init__(); self.ids=[]; self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='a' and 'href' in a: self.hrefs.append(a['href'])
class KnowledgeSubstrateProposalTests(unittest.TestCase):
    def test_proposed_schemas_are_json(self):
        d=ROOT/'docs/proposals'/'research-knowledge-substrate'/'schemas'
        files=sorted(d.glob('*.json'))
        self.assertEqual(len(files),5)
        for p in files:
            obj=json.loads(p.read_text(encoding='utf-8'))
            self.assertIn('$schema',obj)
            self.assertIn('PROPOSED',obj.get('title',''))
    def test_documents_structurally_clean(self):
        d=ROOT/'docs/archive/refresh-editions'/'2026-08-11'/'research-knowledge-substrate'
        files=sorted(d.glob('*.html')); self.assertEqual(len(files),2)
        for p in files:
            txt=p.read_text(encoding='utf-8'); self.assertNotIn('�',txt)
            parser=P(); parser.feed(txt)
            self.assertEqual(len(parser.ids),len(set(parser.ids)))
            ids=set(parser.ids)
            for h in parser.hrefs:
                if h.startswith('#'): self.assertIn(h[1:],ids)
    def test_accepted_for_refinement_is_recorded(self):
        p=ROOT/'catalog'/'RESEARCH_DOCUMENT_RELATIONSHIP_SECTION-vNext-PROPOSED.md'
        txt=p.read_text(encoding='utf-8')
        self.assertIn('ACCEPTED FOR REFINEMENT',txt)
        self.assertIn('machine-readable',txt.lower())
if __name__=='__main__': unittest.main()
