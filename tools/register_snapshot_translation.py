#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'catalog'/'CANONICAL_SNAPSHOT_RESEARCH_INDEX.json'
SRCROOT=ROOT/'corpus'/'canonical-snapshot'/'2026-08-05'/'docs'/'research'
TRROOT=ROOT/'corpus'/'canonical-snapshot'/'2026-08-05'/'translations'/'en'/'docs'/'research'
MANROOT=ROOT/'corpus'/'canonical-snapshot'/'2026-08-05'/'translation-manifests'/'en'
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''): h.update(c)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('source_rel'); ap.add_argument('translation_file'); args=ap.parse_args()
 rel=Path(args.source_rel); src=SRCROOT/rel; supplied=Path(args.translation_file)
 if not src.is_file(): raise SystemExit(f'source not found: {src}')
 if not supplied.is_file(): raise SystemExit(f'translation not found: {supplied}')
 idx=json.loads(INDEX.read_text(encoding='utf-8')); item=next((x for x in idx['items'] if x['sourcePath']=='docs/research/'+rel.as_posix()),None)
 if not item: raise SystemExit('source not in snapshot index')
 if sha(src)!=item['sha256']: raise SystemExit('source hash drift')
 suffix=''.join(rel.suffixes) or '.txt'; stem=rel.name[:-len(suffix)] if suffix else rel.name
 out=TRROOT/rel.parent/(stem+'.en'+suffix); out.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(supplied,out)
 trsha=sha(out)
 trrel=out.relative_to(ROOT).as_posix()
 item['englishTranslationPath']=trrel; item['translationStatus']='MACHINE_TRANSLATED_UNREVIEWED'; item['translationSha256']=trsha
 INDEX.write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 mf={'schemaVersion':'1.0','baselineId':idx['baselineId'],'sourcePath':item['preservedPath'],'sourceSha256':item['sha256'],'sourceLanguage':item['nativeLanguage'],'translationLanguage':'en','translationPath':trrel,'translationSha256':trsha,'translationStatus':'MACHINE_TRANSLATED_UNREVIEWED','authority':'DERIVATIVE_NON_AUTHORITATIVE'}
 mpath=MANROOT/rel.parent/(rel.name+'.translation.json'); mpath.parent.mkdir(parents=True,exist_ok=True); mpath.write_text(json.dumps(mf,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(mf,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
