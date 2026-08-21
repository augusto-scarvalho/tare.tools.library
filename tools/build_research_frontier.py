from __future__ import annotations
from pathlib import Path
import json, re, hashlib, html, unicodedata, difflib
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]
FR = ROOT/'catalog/frontier'
DATE='2026-08-11'

for d in [FR, FR/'pointers', FR/'clusters', FR/'by-lineage', FR/'decisions']:
    d.mkdir(parents=True, exist_ok=True)

LINEAGES = {
 'agent-os-foundations':'Agent OS Foundations',
 'workflow-procedural':'Workflow & Procedural Systems',
 'context-memory-playbooks':'Context, Memory & Playbooks',
 'assurance-governance-quality':'Assurance, Governance & Quality',
 'runtime-reliability-sandbox':'Runtime, Reliability & Sandbox',
 'routing-economics-observability':'Routing, Economics & Observability',
 'interoperability-protocols':'Interoperability & Protocols',
 'experience-ux':'Experience, TUI & UX',
 'research-methodology-evidence':'Research Methodology & Evidence',
}

SECTION_MAP = {
 'Workflow and procedural systems': ('workflow-procedural','workflow-procedural'),
 'Reliability, effects, and durable runtime': ('runtime-reliability-sandbox','reliability-effects-durable-runtime'),
 'Assurance, audit, and evaluator metrology': ('assurance-governance-quality','assurance-audit-metrology'),
 'Governance and constitutional questions': ('assurance-governance-quality','governance-constitutional'),
 'Routing, reputation, and economics': ('routing-economics-observability','routing-reputation-economics'),
 'Runtime, interoperability, and identity': ('interoperability-protocols','runtime-interop-identity'),
 'Context, memory, and project understanding': ('context-memory-playbooks','context-memory-project'),
 'UX / Experience Plane': ('experience-ux','experience-ux'),
 'Local models and empirical harness evaluation': ('routing-economics-observability','local-models-evaluation'),
 'Cross-disciplinary research bridges': ('research-methodology-evidence','cross-disciplinary-bridges'),
 'Research Knowledge Substrate / scholarly data enrichment': ('research-methodology-evidence','research-knowledge-substrate'),
}

REFRESH_CLUSTER_BY_LINEAGE = {
 'agent-os-foundations':'agent-os-foundations',
 'workflow-procedural':'workflow-procedural',
 'context-memory-playbooks':'context-memory-project',
 'assurance-governance-quality':'assurance-audit-metrology',
 'runtime-reliability-sandbox':'reliability-effects-durable-runtime',
 'routing-economics-observability':'routing-reputation-economics',
 'interoperability-protocols':'runtime-interop-identity',
 'experience-ux':'experience-ux',
 'research-methodology-evidence':'research-methodology-evidence',
}

CLUSTER_LABELS = {
 'workflow-procedural':'Workflow & Procedural Systems',
 'reliability-effects-durable-runtime':'Reliability, Effects & Durable Runtime',
 'assurance-audit-metrology':'Assurance, Audit & Evaluator Metrology',
 'governance-constitutional':'Governance & Constitutional Questions',
 'routing-reputation-economics':'Routing, Reputation & Economics',
 'runtime-interop-identity':'Runtime, Interoperability & Identity',
 'context-memory-project':'Context, Memory & Project Understanding',
 'experience-ux':'UX / Experience Plane',
 'local-models-evaluation':'Local Models & Empirical Harness Evaluation',
 'cross-disciplinary-bridges':'Cross-disciplinary Research Bridges',
 'research-knowledge-substrate':'Research Knowledge Substrate',
}

STATUS = {'DISCOVERED','NORMALIZED','TRIAGED','ACTIVE_RESEARCH','EVIDENCE_ACCUMULATING','SYNTHESIZED','OPEN','REJECTED','INCONCLUSIVE','FINDING_CANDIDATE','DORMANT','DUPLICATE','SUBSUMED','RESOLVED'}
RADAR = {'WATCH','EXPLORE','INVESTIGATE','EXPERIMENT','SYNTHESIZE','READY_FOR_RECONCILIATION'}
AUTH='RESEARCH_ONLY_NO_IMPLEMENTATION_AUTHORITY'

def norm(s:str)->str:
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    s=re.sub(r'[^a-z0-9]+',' ',s).strip()
    return re.sub(r'\s+',' ',s)

def slug(s:str)->str:
    return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',norm(s))).strip('-')[:80]

def pid(title:str)->str:
    return 'rp-'+hashlib.sha1(norm(title).encode()).hexdigest()[:10]

def add_candidate(cands, title, description, lineage, cluster, origin, origin_type, source_status='TRIAGED', kind=None):
    title=title.strip().rstrip(' .;:').strip()
    if not title: return
    key=norm(title)
    cands.append({
      'title': title, 'normalized_title': key, 'description': (description or '').strip(),
      'lineage': lineage, 'cluster': cluster, 'origin': origin, 'origin_type': origin_type,
      'source_status': source_status, 'kind': kind or 'research_branch'
    })

cands=[]
# 1) Curated historical/global pointer crosswalk
f=ROOT/'catalog/FUTURE_RESEARCH_POINTERS.md'
section=None
for line_no,line in enumerate(f.read_text(encoding='utf-8').splitlines(),1):
    m=re.match(r'^##\s+\d+\.\s+(.+)$', line)
    if m: section=m.group(1).strip(); continue
    m2=re.match(r'^##\s+(.+)$', line)
    if m2: section=m2.group(1).strip(); continue
    if line.startswith('- '):
        body=line[2:].strip()
        mb=re.match(r'^\*\*(.+?)\*\*\s*[—-]\s*(.+)$', body)
        if mb:
            title,desc=mb.group(1),mb.group(2)
        else:
            title,desc=body,''
        if section in SECTION_MAP:
            lin,cl=SECTION_MAP[section]
        else:
            lin,cl='research-methodology-evidence','cross-disciplinary-bridges'
        kind='bridge' if cl=='cross-disciplinary-bridges' else ('experiment_pointer' if re.search(r'\b(experiment|lab|benchmark|qualification|testing)\b',title,re.I) else 'research_branch')
        add_candidate(cands,title,desc,lin,cl,{'path':f.relative_to(ROOT).as_posix(),'line':line_no,'section':section},'CURATED_POINTER_INDEX','TRIAGED',kind)

# 2) Pointers explicitly in the nine scientific refreshes
refresh_root=ROOT/'refresh-editions/2026-08-11'
for fp in sorted(refresh_root.glob('*/*scientific-refresh-2026-08-11.html')):
    lineage=fp.parent.name
    if lineage not in LINEAGES: continue
    txt=fp.read_text(encoding='utf-8')
    m=re.search(r'<section id="pointers">(.*?)</section>',txt,re.S)
    if not m: continue
    block=m.group(1)
    for li in re.findall(r'<li>(.*?)</li>',block,re.S):
        title=html.unescape(re.sub('<[^>]+>','',li)).strip().rstrip(' .;:').strip()
        kind='experiment_pointer' if re.search(r'\b(experiment|lab|qualification|evaluation|metrology)\b',title,re.I) else 'research_branch'
        add_candidate(cands,title,'',lineage,REFRESH_CLUSTER_BY_LINEAGE[lineage],{'path':fp.relative_to(ROOT).as_posix(),'section':'Research pointers and unresolved bridges'},'SCIENTIFIC_REFRESH_POINTER','NORMALIZED',kind)

# 3) Supplemental meta-research future pointers
fp=refresh_root/'research-knowledge-substrate/research-knowledge-substrate-scientific-ideation-2026-08-11.html'
if fp.exists():
    txt=fp.read_text(encoding='utf-8')
    m=re.search(r'<section id="s19">(.*?)</section>',txt,re.S)
    if m:
        for li in re.findall(r'<li>(.*?)</li>',m.group(1),re.S):
            title=html.unescape(re.sub('<[^>]+>','',li)).strip().rstrip(' .;:').strip()
            kind='bridge' if any(w in norm(title) for w in ['cognitive interoperability','cross project','traceability']) else 'research_branch'
            add_candidate(cands,title,'','research-methodology-evidence','research-knowledge-substrate',{'path':fp.relative_to(ROOT).as_posix(),'section':'Future research pointers'},'META_RESEARCH_POINTER','NORMALIZED',kind)


# 4) New research ingestion pointer packs
for fp in sorted((ROOT/'catalog/NEW_RESEARCH_INGESTIONS').glob('*-pointers.md')) if (ROOT/'catalog/NEW_RESEARCH_INGESTIONS').exists() else []:
    section=None
    for line_no,line in enumerate(fp.read_text(encoding='utf-8').splitlines(),1):
        m=re.match(r'^##\s+(.+)$',line)
        if m: section=m.group(1).strip(); continue
        if not line.startswith('- '): continue
        body=line[2:].strip()
        mb=re.match(r'^\*\*(.+?)\*\*\s*[—-]\s*(.+)$',body)
        if mb: title,desc=mb.group(1),mb.group(2)
        else: title,desc=body,''
        n=norm(title)
        if any(x in n for x in ['workflow','procedural','taskenvelope']): lin,cl='workflow-procedural','workflow-procedural'
        elif any(x in n for x in ['effect','executionattempt','settlement']): lin,cl='runtime-reliability-sandbox','reliability-effects-durable-runtime'
        elif any(x in n for x in ['evaluator','evidence','metrology']): lin,cl='assurance-governance-quality','assurance-audit-metrology'
        elif any(x in n for x in ['identity','federation','principal','workload']): lin,cl='interoperability-protocols','runtime-interop-identity'
        elif any(x in n for x in ['causal','adaptive control']): lin,cl='routing-economics-observability','routing-reputation-economics'
        else: lin,cl='research-methodology-evidence','research-knowledge-substrate'
        kind='experiment_pointer' if any(x in n for x in ['dogfooding','qualification','experiment']) else 'research_branch'
        add_candidate(cands,title,desc,lin,cl,{'path':fp.relative_to(ROOT).as_posix(),'line':line_no,'section':section or 'New research ingestion'},'NEW_RESEARCH_INGESTION_POINTER','TRIAGED',kind)

# Merge exact normalized titles only. Preserve every origin.
bykey=defaultdict(list)
for c in cands: bykey[c['normalized_title']].append(c)
records=[]
for key, items in sorted(bykey.items(), key=lambda kv: kv[0]):
    # canonical title prefers curated index item
    canonical=next((x for x in items if x['origin_type']=='CURATED_POINTER_INDEX'),items[0])
    lineages=sorted(set(x['lineage'] for x in items))
    clusters=sorted(set(x['cluster'] for x in items))
    descriptions=[x['description'] for x in items if x['description']]
    kinds=sorted(set(x['kind'] for x in items))
    # status is TRIAGED if explicitly in curated global pointer list, otherwise NORMALIZED.
    status='TRIAGED' if any(x['origin_type']=='CURATED_POINTER_INDEX' for x in items) else 'NORMALIZED'
    # Transparent radar heuristic, not priority/authority.
    if any(k=='experiment_pointer' for k in kinds): radar='EXPERIMENT'
    elif len(items)>=2: radar='INVESTIGATE'
    elif any(x['origin_type']=='META_RESEARCH_POINTER' for x in items): radar='EXPLORE'
    else: radar='WATCH'
    rec={
      'schema_version':'0.1-proposed',
      'id':pid(canonical['title']),
      'title':canonical['title'],
      'normalized_title':key,
      'status':status,
      'kinds':kinds,
      'description':descriptions[0] if descriptions else '',
      'lineage_ids':lineages,
      'cluster_ids':clusters,
      'origins':[{'path':x['origin']['path'], **({'line':x['origin']['line']} if 'line' in x['origin'] else {}), 'section':x['origin'].get('section',''), 'origin_type':x['origin_type']} for x in items],
      'authority':AUTH,
      'radar_projection':{'bucket':radar,'basis':'derived heuristic from source type, duplicate mentions, and explicit experiment vocabulary; NOT roadmap priority'},
      'curation':{'curated_at':DATE,'priority':'UNTRIAGED','why_not_now':'UNASSESSED','next_action':'TRIAGE_WHEN_REOPENED','human_review':'PENDING'},
      'relations':[],
      'resolution':None,
    }
    records.append(rec)

# Conservative related/possible-duplicate candidates: same lineage, high title similarity, never auto-merge.
for i,a in enumerate(records):
    candidates=[]
    ta=set(a['normalized_title'].split())
    for j,b in enumerate(records):
        if i==j or not (set(a['lineage_ids']) & set(b['lineage_ids'])): continue
        tb=set(b['normalized_title'].split())
        jac=len(ta&tb)/max(1,len(ta|tb))
        seq=difflib.SequenceMatcher(None,a['normalized_title'],b['normalized_title']).ratio()
        score=max(jac,seq)
        if score>=0.58:
            candidates.append((score,b['id'],b['title']))
    for score,bid,btitle in sorted(candidates, reverse=True)[:3]:
        if a['id'] < bid: # avoid duplicate relation pair
            a['relations'].append({'type':'POSSIBLE_OVERLAP_CANDIDATE','target':bid,'confidence':'LOW' if score<0.72 else 'MEDIUM','basis':'lexical-similarity-only-never-auto-merge','score':round(score,3)})

# JSONL
(FR/'RESEARCH_POINTERS.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in records),encoding='utf-8')

# Schemas
schema={
 '$schema':'https://json-schema.org/draft/2020-12/schema','title':'tare.tools.research ResearchPointer','type':'object',
 'required':['schema_version','id','title','normalized_title','status','kinds','lineage_ids','cluster_ids','origins','authority','radar_projection','curation'],
 'properties':{
  'schema_version':{'type':'string'},'id':{'type':'string','pattern':'^rp-[0-9a-f]{10}$'},'title':{'type':'string','minLength':1},
  'normalized_title':{'type':'string','minLength':1},'status':{'enum':sorted(STATUS)},'kinds':{'type':'array','items':{'type':'string'},'minItems':1},
  'description':{'type':'string'},'lineage_ids':{'type':'array','items':{'type':'string'},'minItems':1},'cluster_ids':{'type':'array','items':{'type':'string'},'minItems':1},
  'origins':{'type':'array','minItems':1,'items':{'type':'object','required':['path','origin_type'],'properties':{'path':{'type':'string'},'line':{'type':'integer','minimum':1},'section':{'type':'string'},'origin_type':{'type':'string'}}}},
  'authority':{'const':AUTH},'radar_projection':{'type':'object','required':['bucket','basis'],'properties':{'bucket':{'enum':sorted(RADAR)},'basis':{'type':'string'}}},
  'curation':{'type':'object'},'relations':{'type':'array'},'resolution':{}
 },'additionalProperties':False
}
(ROOT/'schemas/research-pointer.schema.json').write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cluster_schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'ResearchFrontierCluster','type':'object','required':['id','title','pointer_ids','authority'],'properties':{'id':{'type':'string'},'title':{'type':'string'},'pointer_ids':{'type':'array','items':{'type':'string'}},'authority':{'const':AUTH}},'additionalProperties':False}
(ROOT/'schemas/research-frontier-cluster.schema.json').write_text(json.dumps(cluster_schema,indent=2)+'\n',encoding='utf-8')

# Helper link function
byid={r['id']:r for r in records}
def rel_pointer_path(r): return f"pointers/{r['id']}-{slug(r['title'])}.md"

# Individual pointer files
for r in records:
    lines=[f"# {r['id']} — {r['title']}","",f"> **{r['status']} · {r['authority']}**  ","> This pointer is a research-frontier object. It is not a CURRENT gap, TARGET architecture, roadmap commitment, or implementation authorization.","",'## Context']
    if r['description']: lines += ['',r['description']]
    lines += ['', '## Classification', '', f"- **Kinds:** {', '.join(r['kinds'])}", f"- **Lineages:** {', '.join(r['lineage_ids'])}", f"- **Clusters:** {', '.join(r['cluster_ids'])}", f"- **Radar projection:** `{r['radar_projection']['bucket']}` — {r['radar_projection']['basis']}", f"- **Priority:** `{r['curation']['priority']}`", f"- **Why not now:** `{r['curation']['why_not_now']}`", '', '## Origins', '']
    for o in r['origins']:
        loc=f"{o['path']}" + (f":L{o['line']}" if o.get('line') else '')
        lines.append(f"- `{o['origin_type']}` — `{loc}`" + (f" — {o['section']}" if o.get('section') else ''))
    lines += ['', '## Conservative relationship candidates', '']
    if r['relations']:
        for x in r['relations']:
            t=byid[x['target']]
            lines.append(f"- `{x['type']}` → [{t['id']} — {t['title']}](../{rel_pointer_path(t)}) · confidence `{x['confidence']}` · basis `{x['basis']}`")
    else: lines.append('- None generated.')
    lines += ['', '## Rehydration / activation contract', '', 'When this pointer is reopened:', '', '1. locate all origins and relevant lineage documents;', '2. resolve the current canonical architecture epoch and repo truth;', '3. classify prior ideas as `ADOPT / ADAPT / RETIRE / OPEN`;', '4. refresh external scientific evidence separately;', '5. formulate Research Questions / hypotheses / experiments as needed;', '6. only after findings exist, cross the separate Research → Architecture promotion boundary.', '', '## Authority note', '', 'Research pointers preserve intellectual continuity. They do not grant Authority, change policy, ratify TARGET, create a Gap Registry entry, or authorize implementation.', '']
    (FR/rel_pointer_path(r)).write_text('\n'.join(lines),encoding='utf-8')

# clusters
cluster_members=defaultdict(list)
for r in records:
    for c in r['cluster_ids']: cluster_members[c].append(r)
cluster_objects=[]
for cid,members in sorted(cluster_members.items()):
    title=CLUSTER_LABELS.get(cid,LINEAGES.get(cid,cid.replace('-',' ').title()))
    cluster_objects.append({'id':cid,'title':title,'pointer_ids':[r['id'] for r in members],'authority':AUTH})
    lines=[f"# {title}","",'> Research Frontier cluster. Clustering is organizational metadata, not architectural authority.', '', f"Pointers: **{len(members)}**", '', '| Status | Radar | Pointer | Lineages |', '|---|---|---|---|']
    for r in sorted(members,key=lambda x:(x['status'],x['title'].lower())):
        lines.append(f"| `{r['status']}` | `{r['radar_projection']['bucket']}` | [{r['id']} — {r['title']}](../{rel_pointer_path(r)}) | {', '.join(r['lineage_ids'])} |")
    (FR/'clusters'/f'{cid}.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(FR/'RESEARCH_CLUSTERS.json').write_text(json.dumps(cluster_objects,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Lineage views
for lid,label in LINEAGES.items():
    members=[r for r in records if lid in r['lineage_ids']]
    lines=[f"# {label} — Research Frontier","",'> Projection of open research pointers associated with this scientific lineage. It does not define implementation priority.', '', f"Pointers: **{len(members)}**", '', '| Status | Radar | Pointer | Cluster |', '|---|---|---|---|']
    for r in sorted(members,key=lambda x:x['title'].lower()):
        lines.append(f"| `{r['status']}` | `{r['radar_projection']['bucket']}` | [{r['id']} — {r['title']}](../{rel_pointer_path(r)}) | {', '.join(r['cluster_ids'])} |")
    (FR/'by-lineage'/f'{lid}.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

# Indexes
status_counts=Counter(r['status'] for r in records); radar_counts=Counter(r['radar_projection']['bucket'] for r in records)
idx=['# Research Frontier Index','', '> Canonical human projection of `RESEARCH_POINTERS.jsonl`. Research pointers are research-only continuity objects, not CURRENT gaps, TARGET decisions, roadmap commitments, or implementation authorization.', '', f"Total pointers: **{len(records)}**", '', '## Lifecycle', '', '`DISCOVERED → NORMALIZED → TRIAGED → ACTIVE_RESEARCH → EVIDENCE_ACCUMULATING → SYNTHESIZED → FINDING_CANDIDATE`', '', 'Side exits: `DORMANT · DUPLICATE · SUBSUMED · REJECTED · INCONCLUSIVE · RESOLVED · OPEN`.', '', '## Status summary','']
for k,v in sorted(status_counts.items()): idx.append(f'- `{k}`: {v}')
idx += ['', '## Radar projection summary','']
for k,v in sorted(radar_counts.items()): idx.append(f'- `{k}`: {v}')
idx += ['', '## By cluster','']
for c in cluster_objects: idx.append(f"- [{c['title']}](clusters/{c['id']}.md) — {len(c['pointer_ids'])}")
idx += ['', '## By scientific lineage','']
for lid,label in LINEAGES.items(): idx.append(f'- [{label}](by-lineage/{lid}.md)')
idx += ['', '## All pointers','', '| Status | Radar | Pointer | Cluster | Origin count |', '|---|---|---|---|---:|']
for r in sorted(records,key=lambda x:x['title'].lower()): idx.append(f"| `{r['status']}` | `{r['radar_projection']['bucket']}` | [{r['id']} — {r['title']}]({rel_pointer_path(r)}) | {', '.join(r['cluster_ids'])} | {len(r['origins'])} |")
(FR/'FRONTIER_INDEX.md').write_text('\n'.join(idx)+'\n',encoding='utf-8')

# Mobile-friendly HTML projection
rows=[]
for r in sorted(records,key=lambda x:x['title'].lower()):
    pfile=rel_pointer_path(r)
    rows.append(f"<tr><td><code>{html.escape(r['status'])}</code></td><td><code>{html.escape(r['radar_projection']['bucket'])}</code></td><td><a href='{html.escape(pfile)}'>{html.escape(r['id'])} — {html.escape(r['title'])}</a></td><td>{html.escape(', '.join(r['cluster_ids']))}</td><td>{len(r['origins'])}</td></tr>")
cluster_cards=[]
for c in cluster_objects:
    cluster_cards.append(f"<a class='card' href='clusters/{html.escape(c['id'])}.md'><b>{html.escape(c['title'])}</b><span>{len(c['pointer_ids'])} pointers</span></a>")
html_doc=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>tare.tools Research Frontier</title><style>body{{font-family:system-ui,-apple-system,sans-serif;background:#0f1115;color:#e8eaf0;margin:0}}main{{max-width:1180px;margin:auto;padding:28px}}a{{color:#8ab4ff}}.hero{{padding:24px;border:1px solid #303846;border-radius:18px;background:#171b22}}.guard{{border-left:4px solid #e6b450;padding:12px 16px;background:#211d14;margin:18px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:18px 0}}.card{{display:flex;flex-direction:column;gap:5px;padding:14px;text-decoration:none;border:1px solid #303846;border-radius:12px;background:#171b22}}.card span{{color:#aeb7c6;font-size:.9rem}}table{{width:100%;border-collapse:collapse;font-size:.9rem}}th,td{{padding:9px;border-bottom:1px solid #2a303a;text-align:left;vertical-align:top}}code{{color:#b7c9ff}}.meta{{display:flex;gap:10px;flex-wrap:wrap}}.pill{{border:1px solid #364153;border-radius:999px;padding:5px 9px}}@media(max-width:700px){{main{{padding:14px}}table{{font-size:.78rem}}th:nth-child(4),td:nth-child(4){{display:none}}}}</style></head><body><main><section class='hero'><div>tare.tools.research · Experimental Research Knowledge Substrate</div><h1>Research Frontier Registry</h1><p>The explicit boundary of unfinished knowledge: pointers, bridges, experiments and unresolved questions preserved with provenance.</p><div class='meta'><span class='pill'>{len(records)} pointers</span><span class='pill'>{len(cluster_objects)} clusters</span><span class='pill'>{sum(1 for rr in records if len(rr['origins'])>1)} multi-origin</span><span class='pill'>{sum(len(rr['relations']) for rr in records)} overlap candidates</span></div><div class='guard'><b>Authority guardrail.</b> Research Radar and Frontier metadata are research-only projections. They do not create CURRENT gaps, TARGET architecture, roadmap priority or implementation authorization.</div></section><h2>Clusters</h2><div class='grid'>{''.join(cluster_cards)}</div><h2>All pointers</h2><table><thead><tr><th>Status</th><th>Radar</th><th>Pointer</th><th>Cluster</th><th>Origins</th></tr></thead><tbody>{''.join(rows)}</tbody></table></main></body></html>"""
(FR/'RESEARCH_FRONTIER.html').write_text(html_doc,encoding='utf-8')

# Open questions projection
q=['# Open Questions — Research Frontier','', '> This projection lists unresolved research directions. It is not a project backlog.', '']
for lid,label in LINEAGES.items():
    q += [f'## {label}','']
    ms=[r for r in records if lid in r['lineage_ids'] and r['status'] not in {'RESOLVED','REJECTED','SUBSUMED','DUPLICATE'}]
    for r in sorted(ms,key=lambda x:x['title'].lower()): q.append(f"- [{r['id']} — {r['title']}]({rel_pointer_path(r)})" + (f" — {r['description']}" if r['description'] else ''))
    q.append('')
(FR/'OPEN_QUESTIONS.md').write_text('\n'.join(q),encoding='utf-8')

# Dormant/resolved projections (empty initially, explicit)
for name,statuses in [('DORMANT.md',{'DORMANT'}),('RESOLVED.md',{'RESOLVED','SUBSUMED','REJECTED','DUPLICATE'})]:
    ms=[r for r in records if r['status'] in statuses]
    lines=[f"# {name[:-3].title()} Research Pointers",'',f"Count: **{len(ms)}**",'']
    if not ms: lines.append('No pointers currently classified here. This empty projection is deliberate; no status was invented during bootstrap.')
    else:
        for r in ms: lines.append(f"- [{r['id']} — {r['title']}]({rel_pointer_path(r)}) — `{r['status']}`")
    (FR/name).write_text('\n'.join(lines)+'\n',encoding='utf-8')

# possible overlaps report
pairs=[]
for r in records:
    for x in r['relations']:
        pairs.append((x['score'],r,byid[x['target']],x))
lines=['# Possible Duplicate / Overlap Candidates','', '> These are lexical discovery signals only. They are never automatically merged or treated as semantic equivalence.', '', '| Score | Pointer A | Pointer B | Confidence |', '|---:|---|---|---|']
for score,a,b,x in sorted(pairs,reverse=True): lines.append(f"| {score:.3f} | [{a['id']} — {a['title']}]({rel_pointer_path(a)}) | [{b['id']} — {b['title']}]({rel_pointer_path(b)}) | `{x['confidence']}` |")
if not pairs: lines.append('| — | none | none | — |')
(FR/'POSSIBLE_OVERLAPS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

# Radar projection
rad=['# Research Radar — Experimental Projection','', '> `Research Radar` is a generated attention view, not an Authority/roadmap surface. Buckets are heuristic and must not be interpreted as implementation priority.', '']
for bucket in ['READY_FOR_RECONCILIATION','SYNTHESIZE','EXPERIMENT','INVESTIGATE','EXPLORE','WATCH']:
    ms=[r for r in records if r['radar_projection']['bucket']==bucket]
    rad += [f'## {bucket}', '', f'Count: **{len(ms)}**','']
    for r in sorted(ms,key=lambda x:x['title'].lower()): rad.append(f"- [{r['id']} — {r['title']}]({rel_pointer_path(r)})")
    rad.append('')
(FR/'RESEARCH_RADAR.md').write_text('\n'.join(rad),encoding='utf-8')

# Digest
multi=sum(1 for r in records if len(r['origins'])>1)
dig=['# Research Frontier Digest — 2026-08','', '> Generated from the v0.16 Frontier Registry.', '', '## Snapshot','',f'- Total normalized pointers: **{len(records)}**',f'- Pointers with multiple explicit origins: **{multi}**',f'- Conservative possible-overlap pairs: **{len(pairs)}**',f'- Clusters: **{len(cluster_objects)}**',f'- Scientific lineages represented: **{sum(1 for lid in LINEAGES if any(lid in r["lineage_ids"] for r in records))}/9','', '## Radar distribution','']
for k,v in sorted(radar_counts.items()): dig.append(f'- `{k}`: {v}')
dig += ['', '## Epistemic guardrails','', '- Pointer existence ≠ architecture gap.', '- Multiple mentions ≠ priority.', '- Lexical similarity ≠ semantic duplicate.', '- Research Radar ≠ roadmap.', '- Research resolution ≠ automatic TARGET promotion.', '- Reopening requires current repo/architecture reconciliation.', '']
(FR/f'RESEARCH_DIGEST-2026-08.md').write_text('\n'.join(dig),encoding='utf-8')

# Main README
readme=['# Research Frontier Registry','', '> The Frontier Registry preserves the **boundary of unfinished knowledge** in `tare.tools.research`.', '', 'A Research Pointer is a research-continuity object: it records a question, adjacent branch, contradiction, experiment opportunity or bridge that may deserve later work. It is **not** a CURRENT gap, TARGET architecture, backlog item, ADR, SPEC, Implementation Packet, or authorization.', '', '## Start here','', '- [Frontier Index](FRONTIER_INDEX.md)', '- [Open Questions](OPEN_QUESTIONS.md)', '- [Research Radar](RESEARCH_RADAR.md)', '- [August 2026 Digest](RESEARCH_DIGEST-2026-08.md)', '- [Possible overlap candidates](POSSIBLE_OVERLAPS.md)', '- [Thematic clusters](THEMATIC_CLUSTERS.md)', '', '## Canonical vs projections','', '- `RESEARCH_POINTERS.jsonl` — canonical simple registry representation.', '- `RESEARCH_CLUSTERS.json` — canonical cluster membership metadata for this experimental layer.', '- `pointers/*.md`, indexes, radar and digest — rebuildable human projections.', '', '## Lifecycle','', '`DISCOVERED → NORMALIZED → TRIAGED → ACTIVE_RESEARCH → EVIDENCE_ACCUMULATING → SYNTHESIZED → FINDING_CANDIDATE`', '', 'Side exits: `DORMANT`, `DUPLICATE`, `SUBSUMED`, `REJECTED`, `INCONCLUSIVE`, `RESOLVED`, `OPEN`.', '', '## Promotion boundary','', 'A pointer may lead to a Research Question, hypothesis, study, evidence and finding. Only after that work exists may a separate promotion path consider `ADOPT / ADAPT / RETIRE / OPEN`, ADR/SPEC/BDD or an Implementation Packet.', '', '## Harvesting policy','', 'The v0.16 harvester imports only **explicit pointer surfaces**: the curated historical pointer crosswalk, the nine scientific-refresh pointer sections, and the supplemental Research Knowledge Substrate future-research section. It deliberately does not turn every occurrence of “unresolved”, “question”, or “future” in prose/logs into a pointer.', '']
(FR/'README.md').write_text('\n'.join(readme),encoding='utf-8')

# Thematic clusters index
th=['# Thematic Research Clusters','', '> Clusters group pointers without erasing pointer identity. They are navigational/research-program projections.', '']
for c in cluster_objects: th.append(f"- [{c['title']}](clusters/{c['id']}.md) — {len(c['pointer_ids'])} pointers")
(FR/'THEMATIC_CLUSTERS.md').write_text('\n'.join(th)+'\n',encoding='utf-8')

# Decision record
(FR/'decisions'/f'{DATE}-frontier-registry-adoption.md').write_text(f'''# Research Frontier Registry — Adoption Decision\n\n**Date:** {DATE}\n**Status:** ACCEPTED_FOR_EXPERIMENTAL_OPERATION_IN_RESEARCH_REPOSITORY\n\nThe project owner accepted the Research Frontier model for organized handling of pointers left across chats and documents.\n\nThis acceptance authorizes implementation of the **research metadata/workflow inside `tare.tools.research`**. It does not ratify new Agent OS primitives, architecture, roadmap priority or implementation tasks.\n\n## Accepted operating model\n\n- preserve pointer origin/context;\n- distinguish Pointer → Research Question → Hypothesis → Study → Finding;\n- preserve lifecycle rather than OPEN/CLOSED only;\n- cluster without deleting specificity;\n- harvest explicit pointer surfaces automatically;\n- keep promotion/merge semantic curation conservative;\n- expose Radar/Digest as projections only;\n- preserve `why_not_now`, resolution and reopen triggers when curated later;\n- integrate an `Open Research Frontier` section in shadow relationship capsules before making it mandatory in all research documents.\n''',encoding='utf-8')

# Shadow integration: append/rebuild Open Research Frontier in 9 relationship capsules.
capdir=ROOT/'catalog/relationship-capsules'
for lid,label in LINEAGES.items():
    cap=capdir/f'{lid}.md'
    if not cap.exists(): continue
    txt=cap.read_text(encoding='utf-8')
    txt=re.sub(r'\n## Open Research Frontier \(shadow\).*?(?=\n## |\Z)','',txt,flags=re.S)
    ms=[r for r in records if lid in r['lineage_ids']]
    sect=['','## Open Research Frontier (shadow)','', '> Accepted for experimental refinement. This section links to the Research Frontier Registry; it does not make any pointer a canonical gap or implementation task.','']
    for r in sorted(ms,key=lambda x:x['title'].lower()):
        rel=Path('..')/'..'/'frontier'/rel_pointer_path(r)
        sect.append(f"- [{r['id']} — {r['title']}]({rel.as_posix()}) · `{r['status']}` · radar `{r['radar_projection']['bucket']}`")
    cap.write_text(txt.rstrip()+'\n'+'\n'.join(sect)+'\n',encoding='utf-8')

# Update document standard vNext proposal to include accepted 8th block in shadow.
std=ROOT/'catalog/RESEARCH_DOCUMENT_STANDARD-vNEXT-PROPOSAL.md'
if std.exists():
    s=std.read_text(encoding='utf-8')
    marker='## Research Frontier extension — accepted for refinement'
    if marker not in s:
        s += f'''\n\n{marker}\n\nFor scientific/exploratory documents, add an eighth relationship section in shadow:\n\n**8. Open Research Frontier** — explicit unresolved questions, research pointers, contradictions, experiment opportunities, bridge topics and reopen triggers.\n\nThe seven accepted relationship blocks describe what a work *is and relates to*; the eighth describes what it **does not yet resolve**. Pointer IDs should link to `frontier/` when available. This extension is accepted for refinement but remains a research-documentation convention, not an Agent OS primitive.\n'''
        std.write_text(s,encoding='utf-8')

# Acceptance file extension
acc=ROOT/'catalog/RESEARCH_LINEAGE_INFLUENCE_vNEXT_ACCEPTED_FOR_REFINEMENT.md'
if acc.exists():
    s=acc.read_text(encoding='utf-8')
    if 'Open Research Frontier' not in s:
        s += '\n\n## Frontier extension accepted for experimental refinement\n\nAn optional eighth block, **Open Research Frontier**, links document-local future work to the global `frontier/` registry without turning those pointers into roadmap or architecture authority.\n'
        acc.write_text(s,encoding='utf-8')

print(json.dumps({'candidates':len(cands),'normalized_pointers':len(records),'clusters':len(cluster_objects),'multi_origin':multi,'overlap_pairs':len(pairs),'status':dict(status_counts),'radar':dict(radar_counts)},indent=2))
