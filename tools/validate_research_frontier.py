#!/usr/bin/env python3
from pathlib import Path
import json,re,html,sys

ROOT=Path(__file__).resolve().parents[1]
FR=ROOT/'frontier'
ALLOWED_STATUS={'DISCOVERED','NORMALIZED','TRIAGED','ACTIVE_RESEARCH','EVIDENCE_ACCUMULATING','SYNTHESIZED','OPEN','REJECTED','INCONCLUSIVE','FINDING_CANDIDATE','DORMANT','DUPLICATE','SUBSUMED','RESOLVED'}
ALLOWED_RADAR={'WATCH','EXPLORE','INVESTIGATE','EXPERIMENT','SYNTHESIZE','READY_FOR_RECONCILIATION'}
AUTH='RESEARCH_ONLY_NO_IMPLEMENTATION_AUTHORITY'
errs=[]

def norm(s):
    import unicodedata
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9]+',' ',s)).strip()

def strip_title(s): return s.strip().rstrip(' .;:').strip()

reg=FR/'RESEARCH_POINTERS.jsonl'
if not reg.exists(): errs.append('registry missing'); records=[]
else:
    records=[]
    for n,line in enumerate(reg.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip(): continue
        try: records.append(json.loads(line))
        except Exception as e: errs.append(f'invalid jsonl line {n}: {e}')
ids=set(); titles=set()
for r in records:
    rid=r.get('id'); title=r.get('title','')
    if not re.fullmatch(r'rp-[0-9a-f]{10}',rid or ''): errs.append(f'bad id {rid}')
    if rid in ids: errs.append(f'duplicate id {rid}')
    ids.add(rid)
    if not title: errs.append(f'empty title {rid}')
    if r.get('normalized_title') != norm(title): errs.append(f'normalized title mismatch {rid}')
    if r.get('status') not in ALLOWED_STATUS: errs.append(f'bad status {rid}')
    if r.get('authority') != AUTH: errs.append(f'authority mismatch {rid}')
    radar=(r.get('radar_projection') or {}).get('bucket')
    if radar not in ALLOWED_RADAR: errs.append(f'bad radar {rid}')
    if not r.get('origins'): errs.append(f'no origins {rid}')
    for o in r.get('origins',[]):
        p=ROOT/o.get('path','')
        if not p.exists():
            for prefix in ['docs/archive/', 'docs/research/', 'docs/proposals/', 'docs/']:
                cand = ROOT / prefix / o.get('path','')
                if cand.exists(): p = cand; break
                cand_trim = ROOT / prefix / o.get('path','').replace('refresh-editions/', '').replace('incoming/', '').replace('research/', '')
                if cand_trim.exists(): p = cand_trim; break
        if not p.exists(): errs.append(f'origin missing {rid}: {o.get("path")}')
    matches=list((FR/'pointers').glob(f'{rid}-*.md'))
    if len(matches)!=1: errs.append(f'pointer file count {rid}: {len(matches)}')
    elif rid not in matches[0].read_text(encoding='utf-8'): errs.append(f'pointer file content missing id {rid}')

# clusters
cp=FR/'RESEARCH_CLUSTERS.json'
if not cp.exists(): errs.append('cluster metadata missing'); clusters=[]
else:
    try: clusters=json.loads(cp.read_text(encoding='utf-8'))
    except Exception as e: errs.append(f'cluster json invalid {e}'); clusters=[]
for c in clusters:
    if c.get('authority')!=AUTH: errs.append(f'cluster authority {c.get("id")}')
    for rid in c.get('pointer_ids',[]):
        if rid not in ids: errs.append(f'cluster unknown pointer {c.get("id")} {rid}')
    if not (FR/'clusters'/f"{c.get('id')}.md").exists(): errs.append(f'cluster projection missing {c.get("id")}')

# coverage: explicit curated index bullets + 9 refresh pointer sections + supplemental meta-research future section
observed=[]
f=ROOT/'catalog/FUTURE_RESEARCH_POINTERS.md'
section=None
for line in f.read_text(encoding='utf-8').splitlines():
    m=re.match(r'^##\s+(?:\d+\.\s+)?(.+)$',line)
    if m: section=m.group(1).strip(); continue
    if line.startswith('- '):
        body=line[2:].strip(); mb=re.match(r'^\*\*(.+?)\*\*\s*[—-]\s*(.+)$',body)
        title=mb.group(1) if mb else body
        observed.append(norm(strip_title(title)))
for fp in sorted((ROOT/'docs/archive/refresh-editions/2026-08-11').glob('*/*scientific-refresh-2026-08-11.html')):
    if fp.parent.name not in {'agent-os-foundations','workflow-procedural','context-memory-playbooks','assurance-governance-quality','runtime-reliability-sandbox','routing-economics-observability','interoperability-protocols','experience-ux','research-methodology-evidence'}: continue
    txt=fp.read_text(encoding='utf-8'); m=re.search(r'<section id="pointers">(.*?)</section>',txt,re.S)
    if m:
        for li in re.findall(r'<li>(.*?)</li>',m.group(1),re.S): observed.append(norm(strip_title(html.unescape(re.sub('<[^>]+>','',li)))))
meta=ROOT/'refresh-editions/2026-08-11/research-knowledge-substrate/research-knowledge-substrate-scientific-ideation-2026-08-11.html'
if meta.exists():
    txt=meta.read_text(encoding='utf-8'); m=re.search(r'<section id="s19">(.*?)</section>',txt,re.S)
    if m:
        for li in re.findall(r'<li>(.*?)</li>',m.group(1),re.S): observed.append(norm(strip_title(html.unescape(re.sub('<[^>]+>','',li)))))
reg_titles={r.get('normalized_title') for r in records}

# new research ingestion pointer packs
ingdir=ROOT/'catalog/NEW_RESEARCH_INGESTIONS'
if ingdir.exists():
    for fp in sorted(ingdir.glob('*-pointers.md')):
        for line in fp.read_text(encoding='utf-8').splitlines():
            if not line.startswith('- '): continue
            body=line[2:].strip(); mb=re.match(r'^\*\*(.+?)\*\*\s*[—-]\s*(.+)$',body)
            title=mb.group(1) if mb else body
            observed.append(norm(strip_title(title)))
for t in observed:
    if t and t not in reg_titles: errs.append(f'harvest coverage missing: {t}')

# relationship capsules must include shadow frontier and valid links
for cap in sorted((ROOT/'catalog/relationship-capsules').glob('*.md')):
    txt=cap.read_text(encoding='utf-8')
    if '## Open Research Frontier (shadow)' not in txt: errs.append(f'capsule missing frontier {cap.name}')
    for target in re.findall(r'\]\((\.\./\.\./frontier/[^)]+\.md)\)',txt):
        resolved=(cap.parent/target).resolve()
        if not resolved.exists(): errs.append(f'capsule broken frontier link {cap.name}: {target}')

# frontier local markdown links
for md in FR.rglob('*.md'):
    txt=md.read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)#]+\.md)(?:#[^)]+)?\)',txt):
        if '://' in target: continue
        p=(md.parent/target).resolve()
        if not p.exists(): errs.append(f'broken frontier link {md.relative_to(ROOT)} -> {target}')

# guardrails in README/index
for p in [FR/'README.md',FR/'FRONTIER_INDEX.md',FR/'RESEARCH_RADAR.md']:
    txt=p.read_text(encoding='utf-8')
    if 'not' not in txt.lower(): errs.append(f'guardrail prose absent {p.name}')

if errs:
    print('FAIL research frontier')
    for e in errs[:80]: print('-',e)
    if len(errs)>80: print(f'... {len(errs)-80} more')
    raise SystemExit(2)
print(f'PASS research frontier pointers={len(records)} clusters={len(clusters)} explicit_occurrences={len(observed)} links=valid')
