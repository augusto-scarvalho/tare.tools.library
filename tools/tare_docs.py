#!/usr/bin/env python3
"""tare.tools research-document utility. Python stdlib only."""
from pathlib import Path
import argparse, hashlib, json

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024), b''): h.update(c)
 return h.hexdigest()

def load_json(p):
 with open(p,encoding='utf-8') as f:return json.load(f)

def cmd_validate_repo(args):
 root=Path(args.root); errs=[]
 originals=root/'catalog/corpus'/'original'; manifests=root/'catalog/corpus'/'manifests'
 if originals.exists():
  for p in originals.rglob('*'):
   if p.is_file():
    side=manifests/(p.name+'.json')
    if not side.exists(): errs.append(f'missing manifest for {p.relative_to(root)}')
    else:
     m=load_json(side)
     if m.get('provenance',{}).get('source_sha256') != sha256(p): errs.append(f'hash mismatch: {p.relative_to(root)}')
 # Validate translation derivatives without treating them as source authority.
 tmdir=root/'catalog/corpus'/'manifests'/'translations'/'en'
 if tmdir.exists():
  for tp in sorted(tmdir.glob('*.json')):
   tm=load_json(tp)
   src=(root/tm.get('source_path','')) if (root/tm.get('source_path','')).is_file() else (root/'catalog'/tm.get('source_path',''))
   tr=(root/tm.get('translation_path','')) if (root/tm.get('translation_path','')).is_file() else (root/'catalog'/tm.get('translation_path',''))
   if not src.is_file(): errs.append(f'translation source missing: {tp.relative_to(root)}')
   elif tm.get('source_sha256') != sha256(src): errs.append(f'translation source hash mismatch: {tp.relative_to(root)}')
   if not tr.is_file(): errs.append(f'translation file missing: {tp.relative_to(root)}')
   elif tm.get('translation_sha256') != sha256(tr): errs.append(f'translation hash mismatch: {tp.relative_to(root)}')
   if tm.get('source_language')!='pt-BR' or tm.get('target_language')!='en': errs.append(f'translation language contract mismatch: {tp.relative_to(root)}')
 retired=[
  root/'tools/editorial_decision.py',
  root/'.github/workflows/create-publication-pr.yml',
  root/'.github/workflows/editorial-accept.yml',
 ]
 errs += [f'retired central publisher surface still exists: {p.relative_to(root)}' for p in retired if p.exists()]
 publisher=root/'tools/publisher'
 if publisher.exists() and any(path.is_file() for path in publisher.rglob('*')):
  errs.append('retired central publisher surface still contains files: tools/publisher')
 if errs:
  print('\n'.join('ERROR '+e for e in errs)); return 2
 print('PASS repository validation'); return 0

def cmd_rebuild(args):
 root=Path(args.root); manifests=root/'catalog/corpus'/'manifests'; entries=[]
 if manifests.exists():
  for p in sorted(manifests.glob('*.json'),key=lambda p:p.name):
   m=load_json(p); prov=m.get('provenance',{})
   entries.append({
    'document_id':m['document_id'],'title':m['title'],'path':prov.get('source_path',''),'sha256':prov.get('source_sha256',''),'size_bytes':prov.get('size_bytes',0),
    'status':m['status'],'document_type':m['document_type'],'bounded_contexts':m['bounded_contexts'],'created_at':m['created_at'],'origin':prov.get('origin','')})
 cat=root/'catalog'/'MASTER_CATALOG.json'; cat.parent.mkdir(parents=True,exist_ok=True)
 cat.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'WROTE {cat} entries={len(entries)}'); return 0

def main():
 ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
 p=sp.add_parser('validate-repo');p.add_argument('root',nargs='?',default='.');p.set_defaults(fn=cmd_validate_repo)
 p=sp.add_parser('rebuild-catalog');p.add_argument('root',nargs='?',default='.');p.set_defaults(fn=cmd_rebuild)
 a=ap.parse_args(); raise SystemExit(a.fn(a))
if __name__=='__main__': main()
