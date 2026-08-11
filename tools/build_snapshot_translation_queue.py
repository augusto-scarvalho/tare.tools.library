#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'catalog'/'CANONICAL_SNAPSHOT_RESEARCH_INDEX.json'
def main():
 d=json.loads(INDEX.read_text(encoding='utf-8'))
 q=[i for i in d['items'] if i.get('nativeLanguage')!='en' and not i.get('englishTranslationPath')]
 complete=[i for i in d['items'] if i.get('englishTranslationPath')]
 native=[i for i in d['items'] if i.get('nativeLanguage')=='en']
 out={'schemaVersion':'1.1','baselineId':d['baselineId'],'pending':len(q),'translatedDerivatives':len(complete),'nativeEnglish':len(native),'items':q}
 (ROOT/'catalog'/'CANONICAL_SNAPSHOT_TRANSLATION_QUEUE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 md=['# Canonical Snapshot English Translation Queue','',f'Pending: **{len(q)}** exact materialized documents. Already translated derivatives: **{len(complete)}**. Native English sources: **{len(native)}**.','', '| Source | Language | SHA-256 |','|---|---|---|']
 for i in q:
  rel=i['sourcePath'].removeprefix('docs/research/')
  md.append(f"| [{rel}](../{i['preservedPath']}) | `{i['nativeLanguage']}` | `{i['sha256']}` |")
 (ROOT/'catalog'/'CANONICAL_SNAPSHOT_TRANSLATION_QUEUE.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 print(f'PASS snapshot translation queue: pending={len(q)} translated={len(complete)} native_en={len(native)}')
if __name__=='__main__': main()
