#!/usr/bin/env python3
from __future__ import annotations
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import json
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'refresh-editions'/'2026-08-11'
class P(HTMLParser):
    def __init__(self): super().__init__(); self.urls=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='a' and d.get('href','').startswith(('http://','https://')): self.urls.append(d['href'])
def norm(u):
    s=urlsplit(u); q=[(k,v) for k,v in parse_qsl(s.query,keep_blank_values=True) if not k.lower().startswith('utm_')]
    return urlunsplit((s.scheme.lower(),s.netloc.lower(),s.path,s.query and urlencode(q) or '', ''))
def main():
    occ=defaultdict(set)
    for f in sorted(REF.rglob('*.html')):
        p=P(); p.feed(f.read_text(encoding='utf-8'))
        for u in p.urls: occ[norm(u)].add(f.relative_to(REF).as_posix())
    rows=[{'url':u,'domain':urlsplit(u).netloc,'documents':sorted(ds),'document_count':len(ds)} for u,ds in sorted(occ.items())]
    data={'schema_version':'1.0','generated_for':'scientific-refresh-2026-08-11','html_documents':len(list(REF.rglob('*.html'))),'unique_external_urls':len(rows),'sources':rows}
    (REF/'REFRESH_SOURCE_INDEX.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Scientific Refresh External Source Index','',f'HTML documents scanned: **{data["html_documents"]}**. Unique normalized external URLs: **{len(rows)}**.','', '> This is a provenance/navigation index, not an authority ranking. Each scientific refresh contains the interpretation and evidence-grade context.','', '| Source | Domain | Refresh docs |','|---|---|---:|']
    for r in rows: lines.append(f'| [{r["url"]}]({r["url"]}) | `{r["domain"]}` | {r["document_count"]} |')
    (REF/'REFRESH_SOURCE_INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'PASS refresh source index: docs={data["html_documents"]} urls={len(rows)}')
if __name__=='__main__': main()
