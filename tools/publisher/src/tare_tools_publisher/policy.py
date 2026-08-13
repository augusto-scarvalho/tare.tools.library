from pathlib import PurePosixPath

ALLOWED_STATUS={"RESEARCH","PROPOSED","EXPERIMENTAL","HISTORICAL","TARGET","CURRENT"}
CANONICAL_TYPES={"adr","spec","bdd","implementation_packet"}
CONTEXT_DIRS={
 "Workflow":"03_workflow","Routing & Adaptation":"04_routing-reputation","Reputation / Qualification":"04_routing-reputation",
 "Runtime":"05_runtime-model-inference","Model / Inference":"05_runtime-model-inference","Capability / Effects":"06_capabilities-effects",
 "Reliability":"07_reliability","Validation / Assurance":"08_validation-assurance","Evidence / Provenance":"08_validation-assurance",
 "Governance / Audit":"09_governance-audit","Identity / Authority / Policy":"09_governance-audit","Protocols / Interoperability":"10_interoperability-protocols",
 "Project / Workspace":"11_project-workspace","Memory / Context":"12_memory-context","Observability / Economics / Resources":"13_resources-scheduling",
 "Sandbox / Isolation":"14_sandbox-isolation","Experience / Human Interface":"15_experience-tui-repl","Evolution Control":"18_evolution-control"}

def validate(m):
 e=[]
 for k in ["packet_version","document_id","document_type","status","repository","bounded_contexts","artifacts","canonical_change"]:
  if k not in m:e.append(f"missing:{k}")
 if m.get('packet_version') not in {'1.0','1.1'}:e.append('packet_version must be 1.0 or 1.1')
 if m.get('status') not in ALLOWED_STATUS:e.append('invalid status')
 if m.get('repository')=='tare.tools.research' and m.get('status') in {'TARGET','CURRENT'}:e.append('research repo cannot mint TARGET/CURRENT')
 if m.get('document_type') in CANONICAL_TYPES and m.get('repository')!='tare-tools':e.append('canonical type requires tare-tools')
 if m.get('repository')=='tare-tools' and not m.get('canonical_change'):e.append('canonical_change must be true')
 if m.get('repository')=='tare-tools' and not m.get('promotion_packet'):e.append('promotion_packet required')
 if not isinstance(m.get('bounded_contexts'),list) or not m.get('bounded_contexts'):e.append('bounded_contexts required')
 if not isinstance(m.get('artifacts'),list) or not m.get('artifacts'):e.append('artifacts required')
 if 'pages_approved' in m:e.append('pages_approved is editorial authority and must not be submitter-controlled')
 if m.get('packet_version')=='1.1':
  primary=m.get('primary_artifact')
  if not isinstance(primary,str) or primary not in m.get('artifacts',[]):e.append('primary_artifact must be a declared artifact')
  elif not primary.lower().endswith('.html'):e.append('primary_artifact must be canonical HTML')
  if 'document-metadata.json' not in m.get('artifacts',[]):e.append('document-metadata.json must be a declared artifact')
  channels=m.get('requested_channels',[])
  if not isinstance(channels,list) or any(x!='pages' for x in channels):e.append('requested_channels may contain only pages')
 return e

def route(m):
 e=validate(m)
 if e: raise ValueError('; '.join(e))
 if m.get('destination'):
  dest=PurePosixPath(m['destination'])
  if dest.is_absolute() or '..' in dest.parts: raise ValueError('unsafe destination')
  return str(dest)
 t=m['document_type']; did=m['document_id'].replace('.','-'); ctx=CONTEXT_DIRS.get(m['bounded_contexts'][0],'99_unclassified')
 if t=='research':return f'research/{ctx}/{did}'
 if t=='proposal':return f'proposals/architecture/{did}'
 if t=='experiment':return f'experiments/{ctx}/{did}'
 if t in {'archaeology','handoff'}:return f"archaeology/{'implementation-sessions' if t=='handoff' else 'chats'}/{did}"
 if t=='finding':return f'findings/open/{did}'
 if t=='source':return f'sources/community/{did}'
 if t=='adr':return f'docs/adr/{did}'
 if t=='spec':return f'specs/{did}'
 if t=='bdd':return f'testing/{did}'
 if t=='implementation_packet':return f'.harness/handoff/{did}'
 raise ValueError('unsupported type')
