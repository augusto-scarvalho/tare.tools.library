from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
errs=[]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=ROOT/'catalog/corpus/original/2026-08-12-chat-import/Tare.tools - Durable State, Persistence & Consistency Semantics.txt'
expected='39d7c678bb4b87a6f5455f4db4ae0c8a1552f4c3fb40896dc4a66af29758e4e7'
if not source.exists() or sha(source)!=expected: errs.append('exact chat source hash mismatch')
mf=ROOT/'catalog/NEW_RESEARCH_INGESTION-information-survival-demand-lineage-2026-08-12.json'
if not mf.exists(): errs.append('ingestion manifest missing'); m={}
else: m=json.loads(mf.read_text(encoding='utf-8'))
if m.get('status')!='INTEGRATED_AS_CROSS_LINEAGE_RESEARCH_OBJECT': errs.append('bad ingestion status')
refdir=ROOT/'catalog/corpus/library-references/2026-08-12-information-survival-ingestion'
refs=[]
for p in refdir.glob('*.reference.json'):
 o=json.loads(p.read_text(encoding='utf-8')); refs.append(o)
 if not o.get('file_library_id','').startswith('file_'): errs.append(f'bad file library id {p.name}')
 if o.get('availability')!='LIBRARY_REFERENCE_ONLY' or o.get('materialized_bytes') is not False: errs.append(f'bad ref availability {p.name}')
if len(refs)!=6: errs.append(f'expected 6 File Library reference records, got {len(refs)}')
trm=ROOT/'catalog/corpus/manifests/translations/en/Tare.tools - Durable State, Persistence & Consistency Semantics.txt.en.json'
if not trm.exists(): errs.append('translation manifest missing')
else:
 tm=json.loads(trm.read_text(encoding='utf-8'))
 tp=(ROOT/'catalog'/tm['translation_path']) if not (ROOT/tm['translation_path']).exists() else (ROOT/tm['translation_path'])
 if not tp.exists() or sha(tp)!=tm.get('translation_sha256'): errs.append('translation mismatch')
 if tm.get('source_sha256')!=expected: errs.append('translation source identity mismatch')
ro=ROOT/'catalog/research-objects/information-survival-demand-lineage-2026-08-12.json'
if not ro.exists(): errs.append('ResearchObject missing')
else:
 r=json.loads(ro.read_text(encoding='utf-8'))
 if r.get('role')!='cross-lineage-research-object': errs.append('research object role mismatch')
 if len(r.get('lineage_ids',[]))<8: errs.append('insufficient cross-lineage mapping')
for name in ['information-survival-demand-lineage-corpus-integration-review-2026-08-12.html','information-survival-demand-lineage-corpus-integration-review-2026-08-12.en.html','information-survival-demand-lineage-technical-integration-delta-2026-08-12.html','information-survival-demand-lineage-technical-integration-delta-2026-08-12.en.html']:
 p=ROOT/'docs/archive/refresh-editions/2026-08-12/information-survival-demand-lineage'/name
 if not p.exists(): errs.append(f'derived doc missing {name}'); continue
 s=p.read_text(encoding='utf-8'); ids=re.findall(r'\bid="([^"]+)"',s); anchors=re.findall(r'href="#([^"]+)"',s)
 if len(ids)!=len(set(ids)): errs.append(f'duplicate ids {name}')
 if any(a not in set(ids) for a in anchors): errs.append(f'broken anchors {name}')
 if '\ufffd' in s: errs.append(f'utf8 replacement {name}')
g=json.loads((ROOT/'catalog/RESEARCH_RELATION_GRAPH.json').read_text(encoding='utf-8'))
rid='research_object.information-survival-demand-lineage-2026-08-12'; nids={n['id'] for n in g['nodes']}
if rid not in nids: errs.append('research object graph node missing')
rels={(e['to'],e['relation']) for e in g['edges'] if e['from']==rid}
for target in ['lineage.agent-os-foundations','lineage.workflow-procedural','lineage.context-memory-playbooks','lineage.runtime-reliability-sandbox','lineage.assurance-governance-quality','lineage.routing-economics-observability','lineage.interoperability-protocols','lineage.research-methodology-evidence']:
 if not any(t==target for t,r in rels): errs.append(f'cross-lineage edge missing {target}')
reg=[json.loads(x) for x in (ROOT/'catalog/frontier/RESEARCH_POINTERS.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
titles={r['title'] for r in reg}
for title in ['Reconstructive Closure','Demand Accounting & Settlement Science','Independent Semantic Verification of Agent Work','Requirement Clarification as Governed Intake']:
 if title not in titles: errs.append(f'frontier pointer missing {title}')
if errs:
 print('FAIL information survival ingestion'); [print('-',e) for e in errs]; raise SystemExit(2)
print(f'PASS information survival ingestion exact_source={source.stat().st_size}B refs={len(refs)} graph_nodes={len(g["nodes"])} graph_edges={len(g["edges"])} frontier={len(reg)}')
