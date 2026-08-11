#!/usr/bin/env python3
from __future__ import annotations
import json,re
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REF_ROOT=ROOT/"corpus"/"library-references"
OUTJ=ROOT/"catalog"/"LINEAGE_RECONCILIATION.json"
OUTM=ROOT/"catalog"/"LINEAGE_RECONCILIATION.md"
VER=re.compile(r"(?:^|[_-])v(\d+(?:\.\d+)*)",re.I)

def vtuple(s): return tuple(int(x) for x in s.split('.'))

def main():
    items=[]
    for p in REF_ROOT.rglob('*.reference.json'):
        d=json.loads(p.read_text(encoding='utf-8')); d['_path']=p.relative_to(ROOT).as_posix(); items.append(d)
    fam=defaultdict(list); titles=defaultdict(list)
    for d in items:
        if d.get('lineage_family'): fam[d['lineage_family']].append(d)
        titles[d['title']].append(d)
    families=[]
    for name,rows in sorted(fam.items()):
        versions=[]
        for d in rows:
            m=VER.search(d['title'])
            if m: versions.append((vtuple(m.group(1)),m.group(1),d))
        roles={d.get('suggested_kind') for d in rows}
        if len(versions)>=2:
            versions.sort(key=lambda x:x[0])
            status='METADATA_VERSION_SEQUENCE_CONFIRMED_CONTENT_SUPERSESSION_PENDING'
            order=[{'version':v,'file_library_id':d['file_library_id'],'title':d['title']} for _,v,d in versions]
        elif {'research','implementation-proposal'} <= roles or {'research','implementation-research'} <= roles:
            status='SIBLING_ARTIFACT_SET_NOT_SUPERSESSION'
            order=[]
        else:
            status='ORDER_HINT_ONLY_CONTENT_DIFF_REQUIRED'
            order=[]
        families.append({'family':name,'artifact_count':len(rows),'status':status,'version_sequence':order})
    duplicate_titles=[]
    for title,rows in sorted(titles.items()):
        if len(rows)>1:
            duplicate_titles.append({'title':title,'count':len(rows),'file_library_ids':[d['file_library_id'] for d in rows],'status':'IDENTITY_DUPLICATE_UNRESOLVED_EXACT_BYTES_REQUIRED'})
    out={'schema_version':'1.0','principle':'Metadata may establish ordering or sibling roles, but only exact-byte/content comparison may establish supersession or duplicate identity.','families':families,'duplicate_titles':duplicate_titles}
    OUTJ.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    md=['# Lineage Reconciliation','', '> Metadata-only reconciliation. No `supersedes` edge is minted from chronology, title, or filename alone. Exact content remains required for semantic supersession.', '', '## Families','', '| Family | Artifacts | Reconciliation status |','|---|---:|---|']
    for f in families: md.append(f"| `{f['family']}` | {f['artifact_count']} | `{f['status']}` |")
    md += ['', '## Explicit version sequences', '']
    anyseq=False
    for f in families:
        if f['version_sequence']:
            anyseq=True; md.append(f"### `{f['family']}`")
            md.append(' → '.join(f"v{x['version']}" for x in f['version_sequence']))
            md.append('')
            md.append('This is a **version-order fact from filenames**, not yet a proof that each version semantically supersedes the previous one.')
            md.append('')
    if not anyseq: md.append('_None._')
    md += ['','## Duplicate-title identity questions','', '| Title | Count | Status |','|---|---:|---|']
    for d in duplicate_titles: md.append(f"| `{d['title']}` | {d['count']} | `{d['status']}` |")
    OUTM.write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(f"PASS lineage reconciliation: {len(families)} families, {len(duplicate_titles)} duplicate-title groups")
if __name__=='__main__': main()
