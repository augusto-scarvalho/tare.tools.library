#!/usr/bin/env python3
from pathlib import Path
import json, collections
ROOT=Path(__file__).resolve().parents[1]
REFROOT=ROOT/'corpus'/'library-references'
CROSSROOT=ROOT/'catalog'/'identity-crosswalk'
OUTJSON=ROOT/'catalog'/'REHYDRATION_QUEUE.json'
OUTMD=ROOT/'catalog'/'REHYDRATION_QUEUE.md'
OUTLINEAGES=ROOT/'catalog'/'LIBRARY_LINEAGES.md'
OUTCOVERAGE=ROOT/'catalog'/'REHYDRATION_COVERAGE.md'
BASELINE=ROOT/'catalog'/'HISTORICAL_CORPUS_BASELINE.json'
crosswalks={}
if CROSSROOT.exists():
    for cp in sorted(CROSSROOT.glob('*.json')):
        c=json.loads(cp.read_text(encoding='utf-8')); crosswalks[c['file_library_id']]=c
refs=[]
for p in sorted(REFROOT.rglob('*.reference.json')):
    d=json.loads(p.read_text(encoding='utf-8'))
    d['_reference_path']=p.relative_to(ROOT).as_posix()
    d['_materialization']=crosswalks.get(d['file_library_id'])
    refs.append(d)
refs.sort(key=lambda d: (d['priority'], d.get('lineage_family') or '', str(d.get('lineage_order_hint') or ''), d['title'], d['file_library_id']))
summary={
  'schema_version':'1.0',
  'generated_from':'corpus/library-references/**/*.reference.json',
  'total_references':len(refs),
  'identity_crosswalks':sum(1 for r in refs if r.get('_materialization')),
  'pending_materialization':sum(1 for r in refs if not r.get('_materialization')),
  'translation_blocked':sum(1 for r in refs if not r.get('_materialization') and r.get('translation_status')=='BLOCKED_EXACT_SOURCE_NOT_MATERIALIZED'),
  'ready_for_translation':sum(1 for r in refs if r.get('_materialization') and r['_materialization'].get('translation_state')=='READY_FOR_TRANSLATION'),
  'native_english':sum(1 for r in refs if r.get('translation_status')=='NOT_REQUIRED_NATIVE_ENGLISH'),
  'expected_hash_constraints':sum(1 for r in refs if r.get('reported_sha256')),
  'locally_verified_reference_hashes':sum(1 for r in refs if r.get('_materialization') and r.get('reported_sha256')),
  'by_priority':dict(collections.Counter(r['priority'] for r in refs)),
  'items':refs,
}
OUTJSON.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
lines=['# Rehydration Queue','',
'> File Library references are discovery records, not local source bytes. Never reconstruct an "original" from search snippets. Materialize exact source bytes first; then verify identity/hash, import, and only then translate if needed.','',
f"References discovered: **{len(refs)}**. Exact-byte identity crosswalks: **{summary['identity_crosswalks']}**. Expected SHA-256 constraints from independent manifests: **{summary['expected_hash_constraints']}**. Pending materialization: **{summary['pending_materialization']}**. Translation blocked pending exact source: **{summary['translation_blocked']}**. Ready for translation: **{summary['ready_for_translation']}**. Native English: **{summary['native_english']}**.",'',
'## Priority semantics','',
'- **P0** — North Star / architecture / current cross-cutting research needed for reconciliation.','- **P1** — major lineage or high-value research/evidence.','- **P2** — historical versions/supporting artifacts.','- **P3** — low-level evidence/patch history.','']
for pr in ['P0','P1','P2','P3']:
    subset=[r for r in refs if r['priority']==pr and not r.get('_materialization')]
    lines += [f'## {pr} — {len(subset)} item(s)','', '| Artifact | Kind | Family | Language | Translation | File Library ID |', '|---|---|---|---|---|---|']
    for r in subset:
        family=r.get('lineage_family') or '—'
        lang=r.get('native_language') or 'unknown'
        lines.append(f"| **{r['title']}** | `{r['suggested_kind']}` | `{family}` | `{lang}` | `{r['translation_status']}` | `{r['file_library_id']}` |")
    lines.append('')
lines += ['## Materialization protocol','',
'1. Retrieve/open the exact File Library artifact through a supported file surface.','2. Export/materialize its bytes without reconstructing from snippets.','3. Hash the local bytes and compare any `reported_sha256` if present.','4. Import byte-for-byte under `corpus/original/<batch>/`.','5. Preserve the immutable discovery reference and create a separate identity crosswalk plus source provenance manifest; never erase the File Library ID.','6. If source is not English, generate an English derivative under Translation Policy.','7. Run translation QA, navigation, repository validation and checkpoint restore.','']
OUTMD.write_text('\n'.join(lines),encoding='utf-8')
# Discovery-only lineage view. Order hints are not promoted to proven supersession edges.
families=collections.defaultdict(list)
for r in refs:
    if r.get('lineage_family'): families[r['lineage_family']].append(r)
ll=['# File Library Lineage Discovery','',
'> This is a discovery projection, not a canonical supersession graph. `lineage_order_hint` records filename/version/timestamp clues only; exact content comparison is required before asserting `supersedes` / `superseded_by`.','']
for fam, members in sorted(families.items()):
    if len(members) < 2: continue
    members=sorted(members,key=lambda r:(str(r.get('lineage_order_hint') or ''),r.get('file_created_at') or '',r['file_library_id']))
    ll += [f'## `{fam}` — {len(members)} artifact(s)','', '| Order hint | Artifact | Created | File Library ID | Availability |', '|---|---|---|---|---|']
    for r in members:
        ll.append(f"| `{r.get('lineage_order_hint')}` | {r['title']} | `{r.get('file_created_at') or 'unknown'}` | `{r['file_library_id']}` | `{r['availability']}` |")
    ll += ['', '**Review status:** `ORDER_HINT_ONLY — CONTENT_DIFF_REQUIRED`', '']
OUTLINEAGES.write_text('\n'.join(ll),encoding='utf-8')
# Conservative coverage view: current discovery/materialization is not naively equated
# with the historical 102-artifact baseline until identity reconciliation proves it.
b=json.loads(BASELINE.read_text(encoding='utf-8')) if BASELINE.exists() else {}
coverage=['# Rehydration Coverage','', '> Coverage is intentionally conservative. Counts from different discovery surfaces are not added unless identity has been reconciled.','', '## Reported historical baseline','', '| Measure | Reported value | Verification in current runtime |','|---|---:|---|', f"| Archive files | {b.get('reported_archive_file_count','?')} | report only |", f"| Catalogued artifacts | {b.get('reported_catalogued_artifacts','?')} | report only |", f"| Version lineages | {b.get('reported_version_lineages','?')} | report only |", f"| Materialized originals in historical ZIP | {b.get('reported_materialized_original_artifacts','?')} | report only |", f"| File Library references in historical ZIP | {b.get('reported_file_library_reference_artifacts','?')} | report only |", f"| Historical ZIP SHA-256 | `{b.get('reported_archive_sha256','unknown')}` | archive bytes not currently recovered |", '', '## Current bootstrap state','', f"- **11** seed source artifacts are materialized byte-for-byte and have English derivatives.", f"- **{len(refs)}** File Library artifacts are registered as discovery references.", f"- **{summary['identity_crosswalks']}** discovery references have exact-byte identity crosswalks.", f"- **{summary['expected_hash_constraints']}** references already have expected SHA-256/size constraints reported by independent validation manifests (not locally verified source bytes yet).", f"- **{summary['pending_materialization']}** still require exact-byte materialization.", f"- **{summary['translation_blocked']}** translations remain blocked on missing exact source bytes.", f"- **{summary['ready_for_translation']}** newly materialized sources are ready for English translation.", f"- **{summary['native_english']}** discovery references are marked native English.", f"- **{sum(1 for v in families.values() if len(v)>1)}** multi-item lineage families are visible in the discovery projection.", '', '## Why there is no corpus recovery percentage yet','', '`materialized seeds + File Library discovery references` is not a valid recovered-artifact count. Records may overlap the historical corpus, represent later versions, duplicate exports, or multiple artifacts with the same title. Coverage remains:', '', '`NOT_COMPUTABLE_UNTIL_IDENTITY_CROSSWALK`', '', 'The valid path is exact-byte materialization plus identity crosswalk using File Library ID, content hash, reported historical hash, filename, creation time and lineage metadata.']
OUTCOVERAGE.write_text('\n'.join(coverage)+'\n',encoding='utf-8')
print(json.dumps({'references':len(refs),'identity_crosswalks':summary['identity_crosswalks'],'pending_materialization':summary['pending_materialization'],'translation_blocked':summary['translation_blocked'],'ready_for_translation':summary['ready_for_translation'],'native_english':summary['native_english'],'expected_hash_constraints':summary['expected_hash_constraints'],'lineage_families':sum(1 for v in families.values() if len(v)>1)},indent=2))
