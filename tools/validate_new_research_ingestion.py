from pathlib import Path
import json, hashlib, re
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
errs=[]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=ROOT/'corpus/original/2026-08-12-chat-import/Tare.tools - identidade.txt'
expected='b7de23b2ce7e41c1f804b6a8d8c4c5f4a8bb636b056657ec33e6bae3340cc1eb'
if not source.exists() or sha(source)!=expected: errs.append('exact chat source hash mismatch')
manifest=ROOT/'catalog/NEW_RESEARCH_INGESTION-identity-lineage-learning-2026-08-12.json'
if not manifest.exists(): errs.append('ingestion manifest missing'); m={}
else: m=json.loads(manifest.read_text(encoding='utf-8'))
if m.get('status')!='INTEGRATED_AS_CROSS_LINEAGE_RESEARCH_OBJECT': errs.append('bad ingestion status')
# No placeholder/fabricated File Library IDs.
refdir=ROOT/'corpus/library-references/2026-08-12-identity-lineage-ingestion'
refs=[]
for p in refdir.glob('*.reference.json'):
    o=json.loads(p.read_text(encoding='utf-8')); refs.append(o)
    if o['file_library_id']=='file_00000000000000000000000000000000': errs.append(f'placeholder File Library id: {p.name}')
    if o.get('availability')!='LIBRARY_REFERENCE_ONLY' or o.get('materialized_bytes') is not False: errs.append(f'bad reference availability {p.name}')
if len(refs)!=6: errs.append(f'expected 6 materialized File Library reference records, got {len(refs)}')
# English translation sidecar
trm=ROOT/'corpus/manifests/translations/en/Tare.tools - identidade.txt.en.json'
if not trm.exists(): errs.append('translation manifest missing')
else:
    tm=json.loads(trm.read_text(encoding='utf-8')); tp=ROOT/tm['translation_path']
    if not tp.exists() or sha(tp)!=tm.get('translation_sha256'): errs.append('translation manifest mismatch')
    if tm.get('source_sha256')!=expected: errs.append('translation source identity mismatch')

# ResearchObject semantics
ro=ROOT/'catalog/research-objects/identity-lineage-learning-2026-08-12.json'
if not ro.exists(): errs.append('ResearchObject missing')
else:
    r=json.loads(ro.read_text(encoding='utf-8'))
    if r.get('role')!='cross-lineage-research-object': errs.append('research object role mismatch')
    if len(r.get('lineage_ids',[]))<6: errs.append('research object insufficient cross-lineage mapping')
# Derived docs HTML basic structure and duplicate IDs/anchors
for name in ['identity-lineage-learning-corpus-integration-review-2026-08-12.html','identity-lineage-learning-corpus-integration-review-2026-08-12.en.html','identity-lineage-learning-technical-integration-delta-2026-08-12.html','identity-lineage-learning-technical-integration-delta-2026-08-12.en.html']:
    p=ROOT/'refresh-editions/2026-08-12/identity-lineage-learning'/name
    if not p.exists(): errs.append(f'derived doc missing {name}'); continue
    s=p.read_text(encoding='utf-8')
    ids=re.findall(r'\bid="([^"]+)"',s)
    if len(ids)!=len(set(ids)): errs.append(f'duplicate ids {name}')
    anchors=re.findall(r'href="#([^"]+)"',s)
    if any(a not in set(ids) for a in anchors): errs.append(f'broken internal anchors {name}')
    if '\ufffd' in s: errs.append(f'utf8 replacement char {name}')
# Graph must contain research object and cross-lineage relations
g=json.loads((ROOT/'catalog/RESEARCH_RELATION_GRAPH.json').read_text(encoding='utf-8'))
nids={n['id'] for n in g['nodes']}; rid='research_object.identity-lineage-learning-2026-08-12'
if rid not in nids: errs.append('research object graph node missing')
rels={(e['to'],e['relation']) for e in g['edges'] if e['from']==rid}
for target in ['lineage.agent-os-foundations','lineage.workflow-procedural','lineage.runtime-reliability-sandbox','lineage.assurance-governance-quality','lineage.interoperability-protocols','lineage.research-methodology-evidence']:
    if not any(t==target for t,r in rels): errs.append(f'cross-lineage edge missing {target}')
# Frontier source and new specific titles
front_src=ROOT/'catalog/NEW_RESEARCH_INGESTIONS/identity-lineage-learning-2026-08-12-pointers.md'
if not front_src.exists(): errs.append('frontier ingestion source missing')
reg=[json.loads(x) for x in (ROOT/'frontier/RESEARCH_POINTERS.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
titles={r['title'] for r in reg}
for title in ['Minimum Canonical Lineage Contract','ExecutionAttempt identity semantics','Cross-lineage dogfooding of Canonical Lineage']:
    if title not in titles: errs.append(f'frontier pointer missing {title}')
if errs:
    print('FAIL new research ingestion')
    for e in errs: print('-',e)
    raise SystemExit(2)
print(f'PASS new research ingestion exact_source={source.stat().st_size}B refs={len(refs)} graph_nodes={len(g["nodes"])} graph_edges={len(g["edges"])} frontier={len(reg)}')
