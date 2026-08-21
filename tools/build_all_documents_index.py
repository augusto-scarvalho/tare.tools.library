#!/usr/bin/env python3
from __future__ import annotations
import json, os
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]

def rel(base:Path,target:Path)->str:
    return quote(Path(os.path.relpath(target,base)).as_posix(),safe='/._-~')

def main():
    cat=json.loads((ROOT/'catalog'/'MASTER_CATALOG.json').read_text(encoding='utf-8'))
    # translation manifests for the 11 seed originals
    translations={}
    trroot=ROOT/'catalog/corpus'/'manifests'/'translations'/'en'
    if trroot.exists():
        for p in trroot.glob('*.json'):
            d=json.loads(p.read_text(encoding='utf-8')); translations[d['translation_of']]=d
    snap_p=ROOT/'catalog'/'CANONICAL_SNAPSHOT_RESEARCH_INDEX.json'
    snap=json.loads(snap_p.read_text(encoding='utf-8')) if snap_p.exists() else {'items':[]}
    refs_p=ROOT/'catalog'/'REHYDRATION_QUEUE.json'
    refs=json.loads(refs_p.read_text(encoding='utf-8')).get('items',[]) if refs_p.exists() else []
    base=ROOT/'catalog'
    lines=['# All tare.tools Documents & Studies','',
      '> Unified navigation across byte-preserved chat/research originals, exact historical private-GitHub snapshot copies, English derivatives, File Library references, and dated scientific refreshes. Origin and authority are kept explicit.','',
      '## Scientific Refresh — 2026-08-11','',
      '**DERIVED RESEARCH — North Star-directed, not architectural authority.** Historical bytes remain immutable. The 93-file historical research snapshot is curated into 9 scientific lineages, 18 lineage documents, and 2 cross-lineage syntheses.','',
      '- [Start with the refresh README](../refresh-editions/2026-08-11/README.md)',
      '- [Cross-lineage scientific synthesis](../refresh-editions/2026-08-11/tare-tools-scientific-refresh-synthesis-2026-08-11.html)',
      '- [Cross-lineage implementation-research delta](../refresh-editions/2026-08-11/tare-tools-cross-lineage-implementation-research-delta-2026-08-11.html)',
      '- [Historical corpus → refresh crosswalk](../refresh-editions/2026-08-11/REFRESH_CROSSWALK.md)',
      '- [Corpus curation map](../refresh-editions/2026-08-11/CORPUS_CURATION_MAP.md)','',
      '## Live Research Ingestions','',
      '- [2026-08-12 — Identity, Lineage, Learning & Evolution](NEW_RESEARCH_INGESTIONS/identity-lineage-learning-2026-08-12.md) — first formal live-ingestion test; cross-lineage ResearchObject, not a tenth lineage.','',
      '## 1. Materialized chat/research corpus','',
      f'Exact originals: **{len(cat)}**. English derivatives: **{len(translations)}/{len(cat)}**.','',
      '| Document | Status | Contexts | Languages |','|---|---|---|---|']
    for e in cat:
        pt=f"[PT-BR]({rel(base,ROOT/e['path'])})"
        tr=translations.get(e['document_id'])
        en=f"[EN]({rel(base,ROOT/tr['translation_path'])})" if tr else 'EN pending'
        lines.append(f"| **{e['title']}**<br><sub>`{e['document_id']}`</sub> | `{e['status']}` | {', '.join(e.get('bounded_contexts',[]))} | {pt} · {en} |")
    lines += ['', '## 2. Historical private-GitHub snapshot — `docs/research/`','',
      'Baseline: [`baseline.private-github-main.2026-08-05`](../canonical-references/baselines/private-github-main-2026-08-05/README.md). These are exact repository copies from the historical snapshot, not CURRENT.','',
      f"Documents: **{len(snap.get('items',[]))}**.",'',
      '| Repository document | Language | Translation | SHA-256 |','|---|---|---|---|']
    for e in snap.get('items',[]):
        source=ROOT/e['preservedPath']
        lnk=rel(base,source)
        lang=e['nativeLanguage']
        trstate='EN source' if lang=='en' else 'EN pending'
        # optional registered snapshot translation
        trpath=e.get('englishTranslationPath')
        if trpath: trstate=f"[EN]({rel(base,ROOT/trpath)})"
        lines.append(f"| [{e['sourcePath'].removeprefix('docs/research/')}]({lnk}) | `{lang}` | {trstate} | `{e['sha256'][:16]}…` |")
    lines += ['', '## 3. File Library references awaiting exact-byte rehydration','',
      f'References: **{len(refs)}**. These records are discovery metadata only; they are not reconstructed originals.','',
      '| Reference | Language | Priority | Translation state | File Library ID |','|---|---|---|---|---|']
    for e in refs:
        refpath=e.get('_reference_path')
        label=e['title']
        if refpath and (ROOT/refpath).exists(): label=f"[{label}]({rel(base,ROOT/refpath)})"
        lines.append(f"| {label} | `{e.get('native_language','unknown')}` | `{e.get('priority','')}` | `{e.get('translation_status','')}` | `{e.get('file_library_id','')}` |")
    lines += ['', '## Authority rule','',
      '- Historical research, translations, archaeology and File Library references are evidence, not canonical authority.',
      '- The private-GitHub snapshot is a **historical baseline**, not the owner-reported newer dirty CURRENT checkout.',
      '- Promotion to TARGET remains a separate canonical-repository operation.','']
    (ROOT/'catalog'/'ALL_DOCUMENTS_INDEX.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f"PASS all-documents index: seeds={len(cat)} snapshot={len(snap.get('items',[]))} refs={len(refs)}")
if __name__=='__main__': main()
