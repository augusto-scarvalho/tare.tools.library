#!/usr/bin/env python3
from __future__ import annotations
import json,re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
ROOT=Path(__file__).resolve().parents[1]
ORIG=ROOT/'corpus'/'original'
SNAP=ROOT/'corpus'/'canonical-snapshot'/'2026-08-05'/'docs'/'research'
OUTJ=ROOT/'sources'/'SOURCE_INDEX.json'
OUTM=ROOT/'sources'/'SOURCE_INDEX.md'
URL_RE=re.compile(r'https?://[^\s<>"\']+')
TRAIL='.,;:)]}'

def normalize(u):
    u=u.rstrip(TRAIL)
    try:
        p=urlsplit(u); host=p.netloc.lower(); scheme=p.scheme.lower(); path=p.path or '/'
        query=urlencode([(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if not k.lower().startswith('utm_')])
        return urlunsplit((scheme,host,path,query,''))
    except Exception: return u

def docs():
    for p in sorted(ORIG.rglob('*')):
        if p.is_file() and not p.name.endswith('.provenance.json'):
            yield p, 'chat-corpus-original', p.name
    if SNAP.exists():
        for p in sorted(SNAP.rglob('*')):
            if p.is_file():
                yield p, 'private-github-snapshot-2026-08-05', 'docs/research/'+p.relative_to(SNAP).as_posix()

def main():
    index=defaultdict(lambda:{'occurrences':0,'documents':set(),'origins':set()}); count=0; origin_counts=defaultdict(int)
    for p,origin,label in docs():
        count+=1; origin_counts[origin]+=1
        text=p.read_text(encoding='utf-8',errors='replace')
        for raw in URL_RE.findall(text):
            u=normalize(raw)
            if not u: continue
            index[u]['occurrences']+=1; index[u]['documents'].add(label); index[u]['origins'].add(origin)
    rows=[]
    for u,v in sorted(index.items()):
        rows.append({'url':u,'domain':urlsplit(u).netloc.lower(),'occurrences':v['occurrences'],'documents':sorted(v['documents']),'origins':sorted(v['origins'])})
    payload={'schema_version':'1.1','source_scope':'materialized byte-preserved chat originals + exact historical private-GitHub docs/research copies','documents_scanned':count,'origin_counts':dict(origin_counts),'unique_urls':len(rows),'sources':rows}
    OUTJ.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    md=['# Source Index','', '> Deterministic URL projection from materialized byte-preserved sources. It is a navigation/provenance index, not a claim that every URL is still current or authoritative.', '', f'- Documents scanned: **{count}**', f"- Chat corpus originals: **{origin_counts['chat-corpus-original']}**", f"- Historical private-GitHub `docs/research/` copies: **{origin_counts['private-github-snapshot-2026-08-05']}**", f'- Unique URLs: **{len(rows)}**','', '| Domain | URL | Occurrences | Origins | Documents |','|---|---|---:|---|---|']
    for r in rows:
        ds=', '.join(f'`{x}`' for x in r['documents']); origins=', '.join(f'`{x}`' for x in r['origins'])
        md.append(f"| `{r['domain']}` | <{r['url']}> | {r['occurrences']} | {origins} | {ds} |")
    OUTM.write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(f"PASS source index: {count} documents, {len(rows)} unique URLs")
if __name__=='__main__': main()
