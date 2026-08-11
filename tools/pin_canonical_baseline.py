#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,subprocess
from pathlib import Path

def run(repo,*args):
    p=subprocess.run(['git','-C',str(repo),*args],text=True,capture_output=True)
    if p.returncode: raise SystemExit(p.stderr.strip() or 'git failed')
    return p.stdout.strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('repo'); ap.add_argument('--out',default='canonical-references/CANONICAL_BASELINE.json'); ap.add_argument('--path',action='append',default=[]); a=ap.parse_args()
    repo=Path(a.repo).resolve()
    if run(repo,'rev-parse','--is-inside-work-tree')!='true': raise SystemExit('not a git worktree')
    head=run(repo,'rev-parse','HEAD'); branch=run(repo,'branch','--show-current')
    rows=[]
    for rel in a.path:
        p=(repo/rel).resolve()
        if repo!=p and repo not in p.parents: raise SystemExit('path escapes repo')
        if not p.is_file(): raise SystemExit(f'missing canonical path: {rel}')
        rows.append({'path':rel,'sha256':sha(p),'size_bytes':p.stat().st_size})
    out=Path(a.out)
    if not out.is_absolute(): out=Path.cwd()/out
    out.parent.mkdir(parents=True,exist_ok=True)
    payload={'schema_version':'1.0','status':'PINNED_FROM_REAL_GIT_REPOSITORY','repository_path':str(repo),'head':head,'branch':branch,'files':rows}
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(out)
if __name__=='__main__': main()
