#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MAN=ROOT/'corpus'/'manifests'
TMAN=MAN/'translations'/'en'
CROSS=ROOT/'catalog'/'identity-crosswalk'
OUTJ=ROOT/'catalog'/'TRANSLATION_QUEUE.json'
OUTM=ROOT/'catalog'/'TRANSLATION_QUEUE.md'

def load(p): return json.loads(p.read_text(encoding='utf-8'))
translations={}
if TMAN.exists():
    for p in TMAN.glob('*.json'):
        d=load(p); translations[d['translation_of']]=d
cross={}
if CROSS.exists():
    for p in CROSS.glob('*.json'):
        d=load(p); cross[d['document_id']]=d
items=[]
for p in sorted(MAN.glob('*.json')):
    m=load(p); did=m.get('document_id')
    if not did or did in translations: continue
    c=cross.get(did)
    lang=m.get('source_language')
    if not lang and m.get('provenance',{}).get('origin')=='chatgpt-project-session-import': lang='pt-BR'
    if c and c.get('translation_state')=='NOT_REQUIRED_NATIVE_ENGLISH': continue
    if lang and lang.lower() in {'en','en-us','en-gb','english'}: continue
    state='READY_FOR_TRANSLATION' if lang and lang!='unknown' else 'SOURCE_LANGUAGE_REVIEW_REQUIRED'
    items.append({
        'document_id':did,'title':m.get('title'),'source_path':m.get('provenance',{}).get('source_path'),
        'source_sha256':m.get('provenance',{}).get('source_sha256'),'source_language':lang or 'unknown',
        'translation_state':state,'file_library_id':m.get('provenance',{}).get('file_library_id')})
summary={'schema_version':'1.0','target_language':'en','ready':sum(i['translation_state']=='READY_FOR_TRANSLATION' for i in items),'language_review_required':sum(i['translation_state']=='SOURCE_LANGUAGE_REVIEW_REQUIRED' for i in items),'items':items}
OUTJ.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# English Translation Queue','', '> Queue derived only from materialized source bytes. File Library references without exact bytes never enter this queue.', '', f"Ready for EN translation: **{summary['ready']}**. Source-language review required: **{summary['language_review_required']}**.", '', '| Document | Source language | State | Source path |', '|---|---|---|---|']
for i in items:
    lines.append(f"| **{i['title']}**<br><sub>`{i['document_id']}`</sub> | `{i['source_language']}` | `{i['translation_state']}` | `{i['source_path']}` |")
if not items: lines += ['', '_No materialized documents are currently waiting for English translation._']
lines += ['', '## Translation execution contract','', '1. Read the exact materialized source, never a search snippet.', '2. Translate under `TRANSLATION_POLICY.md`; do not modernize or reconcile historical claims.', '3. Write the EN derivative under `corpus/translations/en/<batch>/`.', '4. Create a translation provenance sidecar with source/translation hashes and `MACHINE_TRANSLATED_UNREVIEWED`.', '5. Run structural Translation QA before removing the item from this queue.', '']
OUTM.write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'ready':summary['ready'],'language_review_required':summary['language_review_required']},indent=2))
