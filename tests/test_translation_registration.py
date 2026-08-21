from __future__ import annotations
import hashlib,json
from pathlib import Path
import subprocess,sys,tempfile,unittest
HERE=Path(__file__).resolve().parent
SCRIPT=HERE.parent/'tools'/'register_translation.py'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
class TranslationRegistrationTests(unittest.TestCase):
 def test_registers_derivative_with_source_hash(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'research'; source=root/'catalog/corpus'/'original'/'b'/'study.md'; source.parent.mkdir(parents=True); source.write_text('# PT\ntexto\n',encoding='utf-8')
   mans=root/'catalog/corpus'/'manifests'; mans.mkdir(parents=True)
   sm={'document_id':'research.study','title':'Study','document_type':'research','status':'RESEARCH','created_at':'2026-08-11','source_language':'pt-BR','bounded_contexts':['Workflow'],'provenance':{'origin':'file-library-exact-materialization','source_path':source.relative_to(root).as_posix(),'source_sha256':sha(source),'size_bytes':source.stat().st_size,'original_filename':'study.md'}}
   (mans/'study.md.json').write_text(json.dumps(sm),encoding='utf-8')
   tr=Path(td)/'translation.md';tr.write_text('# EN\ntext\n',encoding='utf-8')
   p=subprocess.run([sys.executable,str(SCRIPT),'--root',str(root),'--document-id','research.study','--translation-file',str(tr)],text=True,capture_output=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
   mps=list((root/'catalog/corpus'/'manifests'/'translations'/'en').glob('*.json'));self.assertEqual(len(mps),1)
   tm=json.loads(mps[0].read_text());self.assertEqual(tm['source_sha256'],sha(source));self.assertEqual(tm['translation_status'],'MACHINE_TRANSLATED_UNREVIEWED');self.assertTrue((root/tm['translation_path']).is_file())
if __name__=='__main__':unittest.main()
