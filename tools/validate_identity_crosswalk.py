#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
CROSS=ROOT/'catalog'/'identity-crosswalk'
REFROOT=ROOT/'catalog/corpus'/'library-references'

def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def load(p): return json.loads(p.read_text(encoding='utf-8'))
refs={}
for p in REFROOT.rglob('*.reference.json'):
 d=load(p); refs[d['file_library_id']]=(d,p)
errors=[]; seen=set(); count=0
for p in sorted(CROSS.glob('*.json')):
 d=load(p); count+=1
 fid=d.get('file_library_id')
 if fid in seen: errors.append(f'duplicate crosswalk file_library_id {fid}')
 seen.add(fid)
 if fid not in refs: errors.append(f'unknown File Library ID {fid}') ; continue
 ref,rp=refs[fid]
 source=ROOT/d.get('source_path','')
 if not source.is_file(): errors.append(f'missing source {d.get("source_path")}')
 elif sha(source)!=d.get('source_sha256'): errors.append(f'hash mismatch {fid}')
 if d.get('reference_id')!=ref.get('reference_id'): errors.append(f'reference_id mismatch {fid}')
 if d.get('reference_path')!=rp.relative_to(ROOT).as_posix(): errors.append(f'reference_path mismatch {fid}')
 reported=ref.get('reported_sha256')
 if reported and reported!=d.get('source_sha256'): errors.append(f'reported hash mismatch {fid}')
 if d.get('reported_hash_verification')== 'MATCH' and not reported: errors.append(f'invalid reported MATCH {fid}')
if errors:
 for e in errors: print('ERROR',e)
 raise SystemExit(2)
print(f'identity crosswalks: {count}/{count} PASS')
