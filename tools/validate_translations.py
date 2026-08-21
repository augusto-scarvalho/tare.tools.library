#!/usr/bin/env python3
"""Structural fidelity checks for derived translations.

These checks do NOT claim semantic/human translation review. They verify that
translation derivatives remain tied to the byte-preserved source and preserve
machine-checkable anchors that should not be lost in translation.
"""
from __future__ import annotations
import collections, hashlib, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'catalog'/'MASTER_CATALOG.json'
TR_MAN=ROOT/'catalog/corpus'/'manifests'/'translations'/'en'
REPORT_MD=ROOT/'catalog'/'TRANSLATION_QA.md'
REPORT_JSON=ROOT/'catalog'/'TRANSLATION_QA.json'

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def urls(s:str): return collections.Counter(re.findall(r'https?://[^\s)\]]+',s))
def ids(s:str): return collections.Counter(re.findall(r'id="([^"]+)"',s))
def cites(s:str): return collections.Counter(re.findall(r'(?:filecite|memcite)[^]*',s))

def main()->int:
    entries=json.loads(CAT.read_text(encoding='utf-8'))
    by_doc={}
    for p in sorted(TR_MAN.glob('*.json')):
        m=json.loads(p.read_text(encoding='utf-8')); by_doc[m['translation_of']]=(p,m)
    rows=[]; failures=[]
    for e in entries:
        doc=e['document_id']; rec={'document_id':doc,'title':e['title']}
        if doc not in by_doc:
            rec.update(status='FAIL', reason='translation_manifest_missing'); failures.append(f'{doc}: translation manifest missing'); rows.append(rec); continue
        mp,m=by_doc[doc]
        src=ROOT/m['source_path']; tr=ROOT/m['translation_path']
        checks={}
        checks['source_exists']=src.is_file(); checks['translation_exists']=tr.is_file()
        if not all(checks.values()):
            rec.update(status='FAIL',checks=checks); failures.append(f'{doc}: source/translation path missing'); rows.append(rec); continue
        a=src.read_text(encoding='utf-8'); b=tr.read_text(encoding='utf-8')
        checks.update({
            'source_hash_matches_manifest': sha(src)==m['source_sha256'],
            'translation_hash_matches_manifest': sha(tr)==m['translation_sha256'],
            'source_catalog_hash_matches': sha(src)==e['sha256'],
            'code_fence_count_preserved': a.count('```')==b.count('```'),
            'code_block_ids_preserved': ids(a)==ids(b),
            'urls_preserved': urls(a)==urls(b),
            'file_memory_citations_preserved': cites(a)==cites(b),
            'replacement_char_count_preserved': a.count('\ufffd')==b.count('\ufffd'),
            'no_truncation_marker': 'The file is too long and its contents have been truncated.' not in b,
        })
        status='PASS' if all(checks.values()) else 'FAIL'
        if status=='FAIL':
            failures.append(f"{doc}: " + ', '.join(k for k,v in checks.items() if not v))
        rec.update(status=status, checks=checks, source_lines=len(a.splitlines()), translation_lines=len(b.splitlines()), source_sha256=sha(src), translation_sha256=sha(tr), review_state=m['translation_status'])
        rows.append(rec)
    report={'schema_version':'1.0','scope':'seed corpus English derivative structural fidelity','semantic_human_review':'NOT_CLAIMED','documents':rows,'summary':{'total':len(rows),'pass':sum(r['status']=='PASS' for r in rows),'fail':sum(r['status']=='FAIL' for r in rows)}}
    REPORT_JSON.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    md=['# Translation QA','', '> Structural fidelity gate only. **PASS does not mean human/semantic review.** It verifies provenance hashes and preservation of URLs, citation tokens, code fences and code-block IDs.','',f"Result: **{report['summary']['pass']}/{report['summary']['total']} PASS**, **{report['summary']['fail']} FAIL**.",'','| Document | Structural QA | Source lines | EN lines | Human review |','|---|---|---:|---:|---|']
    for r in rows:
        md.append(f"| {r['title']} | `{r['status']}` | {r.get('source_lines','—')} | {r.get('translation_lines','—')} | `{r.get('review_state','—')}` |")
    md += ['','## Scope','','This gate intentionally does not modernize, reconcile, fact-check, or silently correct historical claims. Architectural reconciliation is tracked separately.','']
    REPORT_MD.write_text('\n'.join(md),encoding='utf-8')
    if failures:
        print('FAIL translation QA'); [print(' -',f) for f in failures]; return 2
    print(f"PASS translation QA: {len(rows)}/{len(rows)} structural fidelity checks passed")
    return 0
if __name__=='__main__': sys.exit(main())
