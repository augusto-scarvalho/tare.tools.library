#!/usr/bin/env python3
"""Register a completed English derivative against an exact materialized source."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import shutil

ROOT_DEFAULT=Path(__file__).resolve().parents[1]

def sha(p:Path):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()

def load(p): return json.loads(p.read_text(encoding='utf-8'))

def find_manifest(root:Path,did:str):
 matches=[]
 for p in (root/'catalog/corpus'/'manifests').glob('*.json'):
  d=load(p)
  if d.get('document_id')==did: matches.append((d,p))
 if len(matches)!=1: raise ValueError(f'expected exactly one source manifest for {did}, found {len(matches)}')
 return matches[0]

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--document-id',required=True); ap.add_argument('--translation-file',required=True); ap.add_argument('--root',default=str(ROOT_DEFAULT)); ap.add_argument('--batch',default='file-library-translations'); ap.add_argument('--translator',default='OpenAI GPT-5.6 Sol'); ap.add_argument('--translated-at'); ap.add_argument('--target-name')
 a=ap.parse_args(); root=Path(a.root).resolve(); trsrc=Path(a.translation_file).resolve()
 if not trsrc.is_file(): print('DENY translation file missing'); return 2
 try: sm,sp=find_manifest(root,a.document_id)
 except ValueError as e: print('DENY',e); return 2
 source=root/sm['provenance']['source_path']
 if not source.is_file() or sha(source)!=sm['provenance']['source_sha256']: print('DENY source identity/hash invalid'); return 3
 outman=root/'catalog/corpus'/'manifests'/'translations'/'en'; outman.mkdir(parents=True,exist_ok=True)
 for p in outman.glob('*.json'):
  d=load(p)
  if d.get('translation_of')==a.document_id:
   print('DENY translation already registered',p); return 4
 targetdir=root/'catalog/corpus'/'translations'/'en'/a.batch; targetdir.mkdir(parents=True,exist_ok=True)
 name=a.target_name or f"{Path(sm['provenance'].get('original_filename') or source.name).stem}.en{trsrc.suffix or '.md'}"
 target=targetdir/name
 if target.exists(): print('DENY target collision',target); return 4
 shutil.copy2(trsrc,target)
 tsha=sha(target)
 translated_at=a.translated_at or datetime.now(timezone.utc).date().isoformat()
 tm={
  'schema_version':'1.0','translation_id':a.document_id+'.en','translation_of':a.document_id,
  'source_path':source.relative_to(root).as_posix(),'source_sha256':sha(source),
  'translation_path':target.relative_to(root).as_posix(),'translation_sha256':tsha,'translation_size_bytes':target.stat().st_size,
  'source_language':sm.get('source_language') or ('pt-BR' if sm.get('provenance',{}).get('origin')=='chatgpt-project-session-import' else 'unknown'),
  'target_language':'en','translation_status':'MACHINE_TRANSLATED_UNREVIEWED','translator':a.translator,'translated_at':translated_at,
  'policy':'TRANSLATION_POLICY.md','notes':'Faithful derivative translation. Historical claims were not reconciled or silently corrected.'}
 mp=outman/(target.name+'.json'); mp.write_text(json.dumps(tm,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'translation_manifest':mp.relative_to(root).as_posix(),'translation_path':tm['translation_path'],'translation_sha256':tsha},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
