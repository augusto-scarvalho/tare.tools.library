#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'catalog'/'TRANSLATION_QA.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 d=json.loads(QA.read_text(encoding='utf-8')); errs=[]
 if d.get('summary',{}).get('fail')!=0: errs.append('qa report contains failures')
 if d.get('summary',{}).get('pass')!=d.get('summary',{}).get('total'): errs.append('qa report not all pass')
 manifests={}
 for p in (ROOT/'corpus'/'manifests'/'translations'/'en').glob('*.json'):
  m=json.loads(p.read_text(encoding='utf-8')); manifests[m['translation_of']]=m
 for r in d.get('documents',[]):
  m=manifests.get(r['document_id'])
  if not m: errs.append(f"missing translation manifest {r['document_id']}"); continue
  src=ROOT/m['source_path']; tr=ROOT/m['translation_path']
  if not src.is_file() or sha(src)!=r.get('source_sha256'): errs.append(f"source drift {r['document_id']}")
  if not tr.is_file() or sha(tr)!=r.get('translation_sha256'): errs.append(f"translation drift {r['document_id']}")
 if errs:
  print('FAIL'); [print(' -',x) for x in errs]; return 2
 print(f"PASS translation QA snapshot: {d['summary']['pass']}/{d['summary']['total']} hashes unchanged")
 return 0
if __name__=='__main__': raise SystemExit(main())
