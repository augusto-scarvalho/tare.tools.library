#!/usr/bin/env python3
"""tare.tools research-document utility. Python stdlib only."""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, sys

sys.path.insert(0, str(Path(__file__).resolve().parent/'publisher'/'src'))
from tare_tools_publisher.translation import validate_pages_translation

ALLOWED_STATUS={"RESEARCH","PROPOSED","EXPERIMENTAL","HISTORICAL","TARGET","CURRENT"}
RESEARCH_TYPES={"research","proposal","experiment","archaeology","handoff","source","finding"}
CANONICAL_TYPES={"adr","spec","bdd","implementation_packet"}

CONTEXT_DIRS={
 "Workflow":"03_workflow",
 "Routing & Adaptation":"04_routing-reputation",
 "Reputation / Qualification":"04_routing-reputation",
 "Runtime":"05_runtime-model-inference",
 "Model / Inference":"05_runtime-model-inference",
 "Capability / Effects":"06_capabilities-effects",
 "Reliability":"07_reliability",
 "Validation / Assurance":"08_validation-assurance",
 "Evidence / Provenance":"08_validation-assurance",
 "Governance / Audit":"09_governance-audit",
 "Identity / Authority / Policy":"09_governance-audit",
 "Protocols / Interoperability":"10_interoperability-protocols",
 "Project / Workspace":"11_project-workspace",
 "Memory / Context":"12_memory-context",
 "Observability / Economics / Resources":"13_resources-scheduling",
 "Sandbox / Isolation":"14_sandbox-isolation",
 "Experience / Human Interface":"15_experience-tui-repl",
 "Evolution Control":"18_evolution-control",
}

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024), b''): h.update(c)
 return h.hexdigest()

def load_json(p):
 with open(p,encoding='utf-8') as f:return json.load(f)

def validate_manifest(m):
 errors=[]
 for k in ["packet_version","document_id","document_type","status","repository","bounded_contexts","artifacts","canonical_change"]:
  if k not in m: errors.append(f"missing:{k}")
 if m.get("packet_version") not in {"1.0","1.1"}: errors.append("packet_version must be 1.0 or 1.1")
 if m.get("status") not in ALLOWED_STATUS: errors.append("invalid status")
 if m.get("repository") not in {"tare.tools.research","tare-tools"}: errors.append("invalid repository")
 if not isinstance(m.get("bounded_contexts"),list) or not m.get("bounded_contexts"): errors.append("bounded_contexts required")
 if not isinstance(m.get("artifacts"),list) or not m.get("artifacts"): errors.append("artifacts required")
 if "pages_approved" in m: errors.append("pages_approved is editorial authority and must not be submitter-controlled")
 if m.get("packet_version")=="1.1":
  primary=m.get("primary_artifact")
  if not isinstance(primary,str) or primary not in m.get("artifacts",[]): errors.append("primary_artifact must be a declared artifact")
  elif not primary.lower().endswith(".html"): errors.append("primary_artifact must be canonical HTML")
  if "document-metadata.json" not in m.get("artifacts",[]): errors.append("document-metadata.json must be a declared artifact")
  channels=m.get("requested_channels",[])
  if not isinstance(channels,list) or any(x!="pages" for x in channels): errors.append("requested_channels may contain only pages")
 # Authority/promotion boundaries
 if m.get("repository")=="tare.tools.research" and m.get("status") in {"TARGET","CURRENT"}:
  errors.append("research repo cannot mint TARGET/CURRENT")
 if m.get("document_type") in CANONICAL_TYPES and m.get("repository")!="tare-tools":
  errors.append("canonical document types require tare-tools")
 if m.get("repository")=="tare-tools" and m.get("canonical_change") is not True:
  errors.append("tare-tools publication requires canonical_change=true")
 if m.get("repository")=="tare-tools" and not m.get("promotion_packet"):
  errors.append("canonical publication requires promotion_packet")
 return errors

def route(m):
 errs=validate_manifest(m)
 if errs: raise ValueError('; '.join(errs))
 if m.get('destination'): return m['destination']
 t=m['document_type']; ctx=m['bounded_contexts'][0]
 c=CONTEXT_DIRS.get(ctx, '99_unclassified')
 did=m['document_id'].replace('.','-')
 if t=='research': return f"research/{c}/{did}"
 if t=='proposal': return f"proposals/architecture/{did}"
 if t=='experiment': return f"experiments/{c}/{did}"
 if t in {'archaeology','handoff'}: return f"archaeology/{'implementation-sessions' if t=='handoff' else 'chats'}/{did}"
 if t=='source': return f"sources/community/{did}"
 if t=='finding': return f"findings/open/{did}"
 if t=='adr': return f"docs/adr/{did}"
 if t=='spec': return f"specs/{did}"
 if t=='bdd': return f"testing/{did}"
 if t=='implementation_packet': return f".harness/handoff/{did}"
 raise ValueError('unsupported document type')

def cmd_validate(args):
 m=load_json(args.manifest); errs=validate_manifest(m)
 if errs:
  for e in errs: print('ERROR',e)
  return 2
 print('PASS', route(m)); return 0

def cmd_route(args):
 print(route(load_json(args.manifest))); return 0

def cmd_validate_repo(args):
 root=Path(args.root); errs=[]
 originals=root/'corpus'/'original'; manifests=root/'corpus'/'manifests'
 if originals.exists():
  for p in originals.rglob('*'):
   if p.is_file():
    side=manifests/(p.name+'.json')
    if not side.exists(): errs.append(f'missing manifest for {p.relative_to(root)}')
    else:
     m=load_json(side)
     if m.get('provenance',{}).get('source_sha256') != sha256(p): errs.append(f'hash mismatch: {p.relative_to(root)}')
 # Validate translation derivatives without treating them as source authority.
 tmdir=root/'corpus'/'manifests'/'translations'/'en'
 if tmdir.exists():
  for tp in sorted(tmdir.glob('*.json')):
   tm=load_json(tp)
   src=root/tm.get('source_path','')
   tr=root/tm.get('translation_path','')
   if not src.is_file(): errs.append(f'translation source missing: {tp.relative_to(root)}')
   elif tm.get('source_sha256') != sha256(src): errs.append(f'translation source hash mismatch: {tp.relative_to(root)}')
   if not tr.is_file(): errs.append(f'translation file missing: {tp.relative_to(root)}')
   elif tm.get('translation_sha256') != sha256(tr): errs.append(f'translation hash mismatch: {tp.relative_to(root)}')
   if tm.get('source_language')!='pt-BR' or tm.get('target_language')!='en': errs.append(f'translation language contract mismatch: {tp.relative_to(root)}')
 incoming_dir=root/'docs/archive/incoming'
 if incoming_dir.exists():
  for p in incoming_dir.rglob('PUBLISH_MANIFEST.json'):
   manifest=load_json(p)
   errs += [f'{p.relative_to(root)}: {x}' for x in validate_manifest(manifest)]
   if manifest.get('packet_version')=='1.1':
    from validate_canonical_html import validate_packet
    errs += [f'{p.relative_to(root)}: {x}' for x in validate_packet(p.parent,manifest)]
    decision_path=p.parent/'EDITORIAL_DECISION.json'
    legacy=False
    if decision_path.is_file():
     try: legacy=load_json(decision_path).get('decision_version')=='1.0'
     except (OSError,json.JSONDecodeError): errs.append(f'{decision_path.relative_to(root)}: invalid editorial decision JSON')
    translation_errors,projection=validate_pages_translation(p.parent,manifest,legacy_decision=legacy)
    errs += [f'{p.relative_to(root)}: {x}' for x in translation_errors]
    if projection:
     from validate_canonical_html import validate_artifacts
     errs += [f'{p.relative_to(root)}: English derivative: {x}' for x in validate_artifacts(p.parent,manifest,projection['primary_artifact'],projection['metadata_artifact'])]
 if errs:
  print('\n'.join('ERROR '+e for e in errs)); return 2
 print('PASS repository validation'); return 0

def cmd_rebuild(args):
 root=Path(args.root); manifests=root/'corpus'/'manifests'; entries=[]
 if manifests.exists():
  for p in sorted(manifests.glob('*.json'),key=lambda p:p.name):
   m=load_json(p); prov=m.get('provenance',{})
   entries.append({
    'document_id':m['document_id'],'title':m['title'],'path':prov.get('source_path',''),'sha256':prov.get('source_sha256',''),'size_bytes':prov.get('size_bytes',0),
    'status':m['status'],'document_type':m['document_type'],'bounded_contexts':m['bounded_contexts'],'created_at':m['created_at'],'origin':prov.get('origin','')})
 cat=root/'catalog'/'MASTER_CATALOG.json'; cat.parent.mkdir(parents=True,exist_ok=True)
 cat.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'WROTE {cat} entries={len(entries)}'); return 0

def cmd_prepare(args):
 root=Path(args.root).resolve(); src=Path(args.document).resolve()
 if not src.is_file(): print('ERROR document not found'); return 2
 safe=args.document_id.replace('.','-')
 packet=root/'docs/archive/incoming'/safe
 if packet.exists(): print('ERROR packet already exists',packet); return 2
 packet.mkdir(parents=True)
 try:
  out=packet/src.name; shutil.copy2(src,out)
  artifacts=[src.name]
  m={
   'packet_version':args.packet_version,'document_id':args.document_id,'document_type':args.document_type,'status':args.status,
   'repository':args.repository,'destination':None,'bounded_contexts':args.context,'artifacts':artifacts,
   'historical_preservation':bool(args.historical_preservation),'canonical_change':bool(args.canonical_change),
   'promotion_packet':args.promotion_packet,'notes':args.notes or ''}
  if args.packet_version=='1.1':
   if src.suffix.lower()!='.html': raise ValueError('packet_version 1.1 requires an HTML primary artifact')
   metadata_src=Path(args.metadata).resolve() if args.metadata else src.parent/'document-metadata.json'
   if not metadata_src.is_file(): raise ValueError('packet_version 1.1 requires --metadata or sibling document-metadata.json')
   shutil.copy2(metadata_src,packet/'document-metadata.json')
   artifacts.append('document-metadata.json')
   m['artifacts']=artifacts
   m['primary_artifact']=src.name
   m['requested_channels']=args.channel or []
  errs=validate_manifest(m)
  if errs: raise ValueError('; '.join(errs))
  (packet/'PUBLISH_MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 except Exception as exc:
  shutil.rmtree(packet,ignore_errors=True)
  print('ERROR',exc); return 2
 print('WROTE',packet/'PUBLISH_MANIFEST.json')
 print('ROUTE',route(m)); return 0

def main():
 ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
 p=sp.add_parser('validate-manifest');p.add_argument('manifest');p.set_defaults(fn=cmd_validate)
 p=sp.add_parser('route');p.add_argument('manifest');p.set_defaults(fn=cmd_route)
 p=sp.add_parser('validate-repo');p.add_argument('root',nargs='?',default='.');p.set_defaults(fn=cmd_validate_repo)
 p=sp.add_parser('rebuild-catalog');p.add_argument('root',nargs='?',default='.');p.set_defaults(fn=cmd_rebuild)
 p=sp.add_parser('prepare-packet');p.add_argument('document');p.add_argument('--root',default='.');p.add_argument('--document-id',required=True);p.add_argument('--document-type',required=True,choices=['research','proposal','experiment','archaeology','handoff','source','finding','adr','spec','bdd','implementation_packet']);p.add_argument('--status',required=True,choices=sorted(ALLOWED_STATUS));p.add_argument('--repository',default='tare.tools.research',choices=['tare.tools.research','tare-tools']);p.add_argument('--context',action='append',required=True);p.add_argument('--packet-version',choices=['1.0','1.1'],default='1.1');p.add_argument('--metadata');p.add_argument('--channel',action='append',choices=['pages']);p.add_argument('--historical-preservation',action='store_true');p.add_argument('--canonical-change',action='store_true');p.add_argument('--promotion-packet');p.add_argument('--notes');p.set_defaults(fn=cmd_prepare)
 a=ap.parse_args(); raise SystemExit(a.fn(a))
if __name__=='__main__': main()
