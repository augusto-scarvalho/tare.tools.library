#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from bs4 import BeautifulSoup
import collections, json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/archive/editorial-editions'/'2026-08-05-private-github-snapshot'
MANIFEST=OUT/'manifests'/'editorial-manifest.json'
QA_JSON=ROOT/'catalog'/'EDITORIAL_QA.json'
QA_MD=ROOT/'catalog'/'EDITORIAL_QA.md'

def main() -> int:
    files=sorted(list((OUT/'source-language').rglob('*.html'))+list((OUT/'en').rglob('*.html')))
    failures=[]; repl=0; dup_total=0; broken_total=0
    for p in files:
        text=p.read_text(encoding='utf-8',errors='strict')
        repl += text.count('\ufffd')
        soup=BeautifulSoup(text,'html.parser')
        ids=[x.get('id') for x in soup.find_all(id=True)]
        dups=[k for k,v in collections.Counter(ids).items() if v>1]
        if dups:
            dup_total += len(dups); failures.append(f'duplicate ids {p.relative_to(OUT)}: {dups[:5]}')
        idset=set(ids)
        broken=[]
        for a in soup.find_all('a',href=True):
            href=a['href']
            if href.startswith('#') and len(href)>1 and href[1:] not in idset:
                broken.append(href[1:])
        if broken:
            broken_total += len(set(broken)); failures.append(f'broken anchors {p.relative_to(OUT)}: {sorted(set(broken))[:5]}')
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    rels=collections.Counter(e['relation'] for e in manifest['entries'])
    source_paths=collections.defaultdict(list)
    for e in manifest['entries']:
        source_paths[e['source_path']].append(e['relation'])
    coverage=[]
    for src,rs in source_paths.items():
        source_editions=rs.count('SOURCE_LANGUAGE_EDITORIAL_EDITION')
        english_editions=sum(r in ('NATIVE_EN_EDITORIAL_EDITION','TRANSLATED_EN_EDITORIAL_EDITION') for r in rs)
        if source_editions!=1 or english_editions!=1:
            coverage.append({'source':src,'relations':rs})
    expected_sources=93
    if len(source_paths)!=expected_sources:
        failures.append(f'expected {expected_sources} unique sources, got {len(source_paths)}')
    if len(list((OUT/'source-language').rglob('*.html')))!=expected_sources:
        failures.append('source-language editorial coverage mismatch')
    if len(list((OUT/'en').rglob('*.html')))!=expected_sources:
        failures.append('English editorial coverage mismatch')
    if repl:
        failures.append(f'UTF-8 replacement characters found: {repl}')
    if coverage:
        failures.append(f'coverage failures: {len(coverage)}')
    att={
        'schemaVersion':'1.0',
        'artifact':'editorial-editions/2026-08-05-private-github-snapshot',
        'htmlFiles':len(files),
        'sourceLanguageEditions':len(list((OUT/'source-language').rglob('*.html'))),
        'englishEditions':len(list((OUT/'en').rglob('*.html'))),
        'manifestEntries':len(manifest['entries']),
        'uniqueHistoricalSources':len(source_paths),
        'relationCounts':dict(rels),
        'replacementCharacters':repl,
        'duplicateIds':dup_total,
        'brokenInternalAnchors':broken_total,
        'coverageFailures':len(coverage),
        'failures':failures,
        'result':'PASS' if not failures else 'FAIL',
    }
    QA_JSON.write_text(json.dumps(att,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    QA_MD.write_text('# Editorial QA\n\n```json\n'+json.dumps(att,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf-8')
    print(json.dumps(att,ensure_ascii=False,indent=2))
    return 0 if not failures else 1

if __name__=='__main__':
    raise SystemExit(main())
