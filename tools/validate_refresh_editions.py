#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REFRESH = ROOT / "refresh-editions" / "2026-08-11"
EXPECTED_HTML = 20
EXPECTED_LINEAGES = 9
EXPECTED_HISTORICAL = 93

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[]; self.hrefs=[]; self.h1=[]; self.headings=[]; self.text=[]
        self._capture_h1=False; self._capture_heading=False
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if 'id' in d: self.ids.append(d['id'])
        if tag=='a' and 'href' in d: self.hrefs.append(d['href'])
        if tag=='h1': self._capture_h1=True
        if tag in {'h2','h3'}: self._capture_heading=True
    def handle_endtag(self, tag):
        if tag=='h1': self._capture_h1=False
        if tag in {'h2','h3'}: self._capture_heading=False
    def handle_data(self, data):
        self.text.append(data)
        if self._capture_h1: self.h1.append(data)
        if self._capture_heading: self.headings.append(data)

def sha256(p:Path):
    h=hashlib.sha256();
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def main():
    errors=[]; warnings=[]; rows=[]
    htmls=sorted(REFRESH.rglob('*.html'))
    if len(htmls)!=EXPECTED_HTML: errors.append(f"html_count={len(htmls)} expected={EXPECTED_HTML}")
    lineage_dirs=[p for p in REFRESH.iterdir() if p.is_dir()]
    if len(lineage_dirs)!=EXPECTED_LINEAGES: errors.append(f"lineage_dirs={len(lineage_dirs)} expected={EXPECTED_LINEAGES}")
    manifest=json.loads((REFRESH/'REFRESH_MANIFEST.json').read_text(encoding='utf-8'))
    if manifest.get('historical_file_count')!=EXPECTED_HISTORICAL: errors.append('historical_file_count mismatch')
    if manifest.get('new_html_count')!=EXPECTED_HTML: errors.append('manifest new_html_count mismatch')
    cross=(REFRESH/'REFRESH_CROSSWALK.md').read_text(encoding='utf-8')
    cross_rows=[l for l in cross.splitlines() if l.startswith('| [`') or l.startswith('| `')]
    if len(cross_rows)!=EXPECTED_HISTORICAL: errors.append(f"crosswalk rows={len(cross_rows)} expected={EXPECTED_HISTORICAL}")

    required_research=['CURRENT','TARGET','PROPOSED','RESEARCH','ADOPT','ADAPT','RETIRE','OPEN','Bibliography']
    required_tech=['PROPOSED','Implementation','Strangler','BDD','evidence']
    for p in htmls:
        raw=p.read_text(encoding='utf-8')
        if '\ufffd' in raw: errors.append(f"replacement char: {p.relative_to(REFRESH)}")
        pr=Parser(); pr.feed(raw)
        dups=sorted({i for i in pr.ids if pr.ids.count(i)>1})
        if dups: errors.append(f"duplicate ids {p.relative_to(REFRESH)}: {dups[:5]}")
        idset=set(pr.ids)
        broken=[]
        for href in pr.hrefs:
            if href.startswith('#') and href[1:] and href[1:] not in idset: broken.append(href)
        if broken: errors.append(f"broken anchors {p.relative_to(REFRESH)}: {sorted(set(broken))[:5]}")
        text=' '.join(pr.text)
        if not ''.join(pr.h1).strip(): errors.append(f"missing h1: {p.relative_to(REFRESH)}")
        kind='technical' if 'implementation-research-delta' in p.name else 'research'
        req=required_tech if kind=='technical' else required_research
        missing=[x for x in req if x.lower() not in text.lower()]
        if missing: errors.append(f"required markers missing {p.relative_to(REFRESH)}: {missing}")
        # All lineage docs must be explicit about evidence-limited CURRENT. Synthesis is allowed a different wording.
        if p.parent != REFRESH:
            lt=text.lower()
            if 'dirty' not in lt or ('repository' not in lt and 'repo' not in lt):
                errors.append(f"CURRENT limitation missing: {p.relative_to(REFRESH)}")
        # URLs should at least be syntactically absolute when external.
        bad_urls=[]
        for href in pr.hrefs:
            if href.startswith(('http://','https://')):
                u=urlparse(href)
                if not u.netloc: bad_urls.append(href)
        if bad_urls: errors.append(f"bad external urls {p.relative_to(REFRESH)}")
        rows.append({'path':p.relative_to(ROOT).as_posix(),'kind':kind,'sha256':sha256(p),'bytes':p.stat().st_size,'ids':len(pr.ids),'hrefs':len(pr.hrefs)})

    # Validate markdown navigation links within refresh README/crosswalk/curation map.
    md_broken=[]
    link_re=re.compile(r'\[[^\]]*\]\(([^)]+)\)')
    for mp in [REFRESH/'README.md', REFRESH/'REFRESH_CROSSWALK.md', REFRESH/'CORPUS_CURATION_MAP.md']:
        txt=mp.read_text(encoding='utf-8')
        for link in link_re.findall(txt):
            if link.startswith(('http://','https://','#','mailto:')): continue
            target=(mp.parent/link.split('#',1)[0]).resolve()
            if not target.exists(): md_broken.append(f"{mp.name}: {link}")
    if md_broken: errors.extend('broken markdown link: '+x for x in md_broken)

    qa={
      'schema_version':'1.0','status':'PASS' if not errors else 'FAIL',
      'html_files':len(htmls),'scientific_lineages':len(lineage_dirs),
      'historical_crosswalk_rows':len(cross_rows),'replacement_chars':0 if not any('replacement char' in e for e in errors) else None,
      'duplicate_ids':[] if not any('duplicate ids' in e for e in errors) else [e for e in errors if 'duplicate ids' in e],
      'broken_internal_anchors':[] if not any('broken anchors' in e for e in errors) else [e for e in errors if 'broken anchors' in e],
      'broken_navigation_links':md_broken,'errors':errors,'warnings':warnings,'documents':rows,
    }
    (REFRESH/'REFRESH_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:qa[k] for k in ['status','html_files','scientific_lineages','historical_crosswalk_rows','broken_navigation_links','errors']},ensure_ascii=False,indent=2))
    return 0 if not errors else 2

if __name__=='__main__': raise SystemExit(main())
