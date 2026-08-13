#!/usr/bin/env python3
"""Build the allowlisted SIGNAL reading projection."""
from __future__ import annotations
import argparse, hashlib, html, json, shutil, subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from validate_canonical_html import validate_packet

ROOT=Path(__file__).resolve().parents[1]; PROFILE=ROOT/'site'/'SIGNAL_PROFILE.json'; ASSETS=ROOT/'site'/'assets'
MEDIA={'.png','.jpg','.jpeg','.webp','.svg','.gif','.mp3','.mp4','.pdf'}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def head(root): return subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],text=True,capture_output=True,check=True).stdout.strip()
def semantic_fingerprint(node):
 payload={'text':node.get_text(' ',strip=True),'ids':[x['id'] for x in node.find_all(id=True)],'headings':[(x.name,x.get('id'),x.get_text(' ',strip=True)) for x in node.find_all(['h1','h2','h3','h4','h5','h6'])],'figures':[x.get_text(' ',strip=True) for x in node.find_all('figure')],'tables':[x.get_text(' ',strip=True) for x in node.find_all('table')],'links':[x.get('href') for x in node.find_all('a',href=True)]}
 return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
def shell(title,nav,body,footer): return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><link rel="stylesheet" href="/assets/signal.css"></head><body><header class="topbar"><span class="mark">tare.tools</span> <span class="sub">research reading projection · SIGNAL</span></header><div class="shell"><nav class="nav">{nav}</nav><main class="article">{body}</main></div><footer class="footer">{footer}</footer><script src="/assets/site.js" defer></script></body></html>'
def build(root: Path, output: Path):
 root=root.resolve(); output=output.resolve(); profile=json.loads(PROFILE.read_text(encoding='utf-8'))
 if output.exists(): shutil.rmtree(output)
 (output/'assets').mkdir(parents=True); [shutil.copy2(ASSETS/name,output/'assets'/name) for name in ('signal.css','site.js')]
 studies=[]; ids=set(); commit=head(root)
 for rp in sorted(root.rglob('PUBLICATION_RECORD.json')):
  record=json.loads(rp.read_text(encoding='utf-8'))
  if record.get('pages_approved') is not True: continue
  packet=rp.parent; manifest=json.loads((packet/'PUBLISH_MANIFEST.json').read_text(encoding='utf-8')); primary=manifest.get('primary_artifact')
  if not primary: raise ValueError(f'{rp}: Pages record lacks primary artifact')
  errors=validate_packet(packet,manifest)
  if errors: raise ValueError(f'{rp}: '+ '; '.join(errors))
  source=packet/primary; expected=record.get('artifact_sha256',{}).get(Path(primary).name)
  if expected!=sha(source): raise ValueError(f'{rp}: primary artifact hash mismatch')
  meta=json.loads((packet/'document-metadata.json').read_text(encoding='utf-8')); did=meta['document_id']; slug=did.replace('.','-')
  if did in ids: raise ValueError(f'duplicate document ID: {did}')
  ids.add(did); target=output/'p'/slug; target.mkdir(parents=True)
  article=BeautifulSoup(source.read_text(encoding='utf-8'),'html.parser').select_one('article[data-tare-document]'); source_fingerprint=semantic_fingerprint(article)
  allowed={Path(x).name for x in manifest['artifacts'] if Path(x).suffix.lower() in MEDIA}
  for tag in article.find_all(src=True):
   name=Path(tag['src']).name
   if name not in allowed: raise ValueError(f'{source}: undeclared asset {tag["src"]}')
   asset=packet/name
   if not asset.is_file(): raise ValueError(f'{source}: missing asset {name}')
   (target/'assets').mkdir(exist_ok=True); shutil.copy2(asset,target/'assets'/name); tag['src']='assets/'+name
  authority=article.select_one('[data-tare-role="authority-boundary"]')
  if authority: authority['class']=authority.get('class',[])+['authority']
  links='<a href="/">Index</a>'+''.join(f'<a href="#{x["id"]}">{html.escape(x.get_text(" ",strip=True))}</a>' for x in article.find_all(['h2','h3']) if x.get('id'))
  instrument=f'<section class="instrument"><span class="status">{html.escape(meta["status"])}</span><br>Canonical SHA-256: <code>{expected}</code><br>Source: <code>{html.escape(source.relative_to(root).as_posix())}</code><br>Signal source: <code>{profile["source_commit"][:12]}</code></section>'
  (target/'index.html').write_text(shell(meta['title'],links,instrument+str(article),f'build {commit} · SIGNAL profile {profile["profile_version"]}'),encoding='utf-8')
  projection={'record_version':'1.0','document_id':did,'source_path':source.relative_to(root).as_posix(),'source_sha256':expected,'build_commit':commit,'signal_profile_sha256':sha(PROFILE),'output_path':f'/p/{slug}/','semantic_fingerprint':source_fingerprint,'transformations':['Signal shell added','TOC generated','declared local assets copied']}
  (target/'PROJECTION_RECORD.json').write_text(json.dumps(projection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  studies.append({'document_id':did,'title':meta['title'],'abstract':meta['abstract'],'status':meta['status'],'url':f'/p/{slug}/'})
 cards=''.join(f'<article data-study><a href="{x["url"]}">{html.escape(x["title"])}</a><p>{html.escape(x["abstract"])}</p><small>{html.escape(x["status"])} · {html.escape(x["document_id"])}</small></article>' for x in studies) or '<p>No research publication is approved for Pages yet.</p>'
 body=f'<section class="instrument"><span class="status">SIGNAL</span><h1>tare.tools research</h1><p>Derived reading projections of editorially approved research HTML.</p><input data-search aria-label="Search publications" placeholder="Search publications"></section><section>{cards}</section>'
 (output/'index.html').write_text(shell('tare.tools research','<a href="/">Index</a>',body,f'build {commit} · allowlisted publication records only'),encoding='utf-8'); (output/'search.json').write_text(json.dumps(studies,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return studies
if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=ROOT); ap.add_argument('--output',type=Path,default=ROOT/'site'/'_site'); args=ap.parse_args(); print(f'PASS Pages build studies={len(build(args.root,args.output))} output={args.output}')
