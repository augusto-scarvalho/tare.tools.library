#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'canonical-references'/'baselines'/'private-github-main-2026-08-05'

def sha_bytes(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def sha_file(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1<<20),b''): h.update(c)
 return h.hexdigest()
def main():
 d=json.loads((BASE/'BASELINE.json').read_text(encoding='utf-8'))
 archive=ROOT/d['source']['preservedPath']
 fails=[]
 if sha_file(archive)!=d['source']['archiveSha256']: fails.append('archive sha mismatch')
 with zipfile.ZipFile(archive) as z:
  infos=[i for i in z.infolist() if not i.is_dir()]; prefix=infos[0].filename.split('/')[0]+'/'
  pairs=[]
  for i in infos:
   rel=i.filename[len(prefix):] if i.filename.startswith(prefix) else i.filename
   pairs.append((rel, f"{sha_bytes(z.read(i))}  {rel}"))
  rows=[row for _,row in sorted(pairs,key=lambda x:x[0])]
  tree=sha_bytes(('\n'.join(rows)).encode())
 if tree!=d['contentIdentity']['treeSha256']: fails.append('content tree sha mismatch')
 if len(rows)!=d['archiveEvidence']['fileCount']: fails.append('file count mismatch')
 expected=(BASE/'TREE_SHA256SUMS.txt').read_text(encoding='utf-8').splitlines()
 if sorted(rows)!=sorted(expected): fails.append('per-file sums mismatch')
 bundle=ROOT/d['syntheticGitImport']['bundlePath']
 if sha_file(bundle)!=d['syntheticGitImport']['bundleSha256']: fails.append('synthetic git bundle sha mismatch')
 if fails:
  for x in fails: print('FAIL',x)
  return 1
 print(f"PASS canonical snapshot: files={len(rows)} archive={d['source']['archiveSha256'][:12]} tree={tree[:12]} bundle={d['syntheticGitImport']['bundleSha256'][:12]}")
 return 0
if __name__=='__main__': raise SystemExit(main())
