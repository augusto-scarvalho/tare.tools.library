from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_pages import build
from validate_pages import validate

HTML='''<!doctype html><html lang="en"><head><title>Study</title></head><body><main><article data-tare-document><header data-tare-role="document-header"><h1>Study</h1><p data-tare-role="abstract">Test abstract.</p></header><aside data-tare-role="authority-boundary">RESEARCH.</aside><section id="scope" data-tare-section="scope"><h2 id="scope-heading">Scope</h2></section><section id="evidence" data-tare-section="evidence"></section><section id="findings" data-tare-section="findings"></section><section id="limitations" data-tare-section="limitations"></section><section id="references" data-tare-section="references"></section></article></main></body></html>'''

class BuildPagesTests(unittest.TestCase):
 def test_only_approved_record_is_projected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); packet=root/'experiments'/'example'; packet.mkdir(parents=True)
   subprocess.run(['git','init','-q',str(root)],check=True)
   (root/'seed').write_text('x'); subprocess.run(['git','-C',str(root),'add','.'],check=True); subprocess.run(['git','-C',str(root),'-c','user.name=t','-c','user.email=t@x.invalid','commit','-qm','seed'],check=True)
   primary=packet/'article.html'; primary.write_text(HTML,encoding='utf-8'); digest=hashlib.sha256(primary.read_bytes()).hexdigest()
   manifest={'packet_version':'1.1','document_id':'research.test.pages','document_type':'research','status':'RESEARCH','repository':'tare.tools.research','bounded_contexts':['Reliability'],'artifacts':['article.html','document-metadata.json'],'primary_artifact':'article.html','requested_channels':['pages'],'pages_approved':True,'canonical_change':False}
   (packet/'PUBLISH_MANIFEST.json').write_text(json.dumps(manifest),encoding='utf-8')
   (packet/'document-metadata.json').write_text(json.dumps({'document_id':'research.test.pages','title':'Study','document_type':'research','status':'RESEARCH','language':'en','abstract':'Test abstract.','authors':[{'name':'Test','role':'editor'}]}),encoding='utf-8')
   (packet/'PUBLICATION_RECORD.json').write_text(json.dumps({'pages_approved':True,'artifact_sha256':{'article.html':digest}}),encoding='utf-8')
   output=root/'site'; studies=build(root,output)
   self.assertEqual([x['document_id'] for x in studies],['research.test.pages'])
   self.assertTrue((output/'p'/'research-test-pages'/'index.html').is_file())
   self.assertEqual(json.loads((output/'search.json').read_text())[0]['status'],'RESEARCH')
   self.assertEqual(json.loads((output/'p'/'research-test-pages'/'PROJECTION_RECORD.json').read_text())['source_sha256'],digest)
   self.assertEqual(validate(output),[])

if __name__=='__main__': unittest.main()
