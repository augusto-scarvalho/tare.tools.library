#!/usr/bin/env python3
"""Build the allowlisted SIGNAL reading projection.

The publisher is a Strangler/compatibility layer:
- an optional pinned incumbent site is copied byte-for-byte first;
- new publication pages are additive under /publications/ and /p/<slug>/;
- the incumbent root/navigation are not replaced until an explicit later cutover;
- every projected study is bound to source hashes, editorial decision evidence,
  deterministic link rewrites and source↔projection semantic parity.
"""
from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

from pages_common import normalize_base_path, semantic_fingerprint, sha256_file, site_url
from validate_canonical_html import validate_packet

ROOT=Path(__file__).resolve().parents[1]
PROFILE=ROOT/'site'/'SIGNAL_PROFILE.json'
INCUMBENT_PROFILE=ROOT/'site'/'INCUMBENT_PROFILE.json'
ASSETS=ROOT/'site'/'assets'
MEDIA={'.png','.jpg','.jpeg','.webp','.svg','.gif','.mp3','.mp4','.pdf'}
PUBLISHED_ROOTS={'research','proposals','experiments','archaeology','sources','findings'}
REPO_SLUG='augusto-scarvalho/tare.tools.research'


def head(root: Path) -> str:
    return subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],text=True,capture_output=True,check=True).stdout.strip()


def _inside(root: Path, candidate: Path) -> bool:
    root=root.resolve(); candidate=candidate.resolve()
    return candidate==root or root in candidate.parents


def _copy_tree(source: Path, output: Path) -> None:
    if output.exists(): shutil.rmtree(output)
    if source:
        shutil.copytree(source,output)
    else:
        output.mkdir(parents=True)


def _publication_records(root: Path) -> list[Path]:
    records=[]
    for rp in root.rglob('PUBLICATION_RECORD.json'):
        rel=rp.relative_to(root)
        if not rel.parts or rel.parts[0] not in PUBLISHED_ROOTS:
            continue
        if any(part.startswith('.') for part in rel.parts):
            continue
        records.append(rp)
    return sorted(records)


def _load_studies(root: Path, commit: str) -> list[dict]:
    studies=[]; ids=set()
    for rp in _publication_records(root):
        record=json.loads(rp.read_text(encoding='utf-8'))
        if record.get('pages_approved') is not True:
            continue
        editorial=record.get('editorial_decision')
        if not isinstance(editorial,dict) or not editorial.get('sha256'):
            raise ValueError(f'{rp}: approved Pages record lacks editorial decision evidence')
        packet=rp.parent
        manifest_path=packet/'PUBLISH_MANIFEST.json'
        decision_path=packet/'EDITORIAL_DECISION.json'
        metadata_path=packet/'document-metadata.json'
        if not manifest_path.is_file(): raise ValueError(f'{rp}: missing PUBLISH_MANIFEST.json')
        if not decision_path.is_file(): raise ValueError(f'{rp}: missing EDITORIAL_DECISION.json')
        if not metadata_path.is_file(): raise ValueError(f'{rp}: missing document-metadata.json')
        manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
        primary=manifest.get('primary_artifact')
        if not primary: raise ValueError(f'{rp}: Pages record lacks primary artifact')
        errors=validate_packet(packet,manifest)
        if errors: raise ValueError(f'{rp}: '+'; '.join(errors))
        source=packet/primary
        expected=record.get('artifact_sha256',{}).get(Path(primary).name)
        if expected!=sha256_file(source): raise ValueError(f'{rp}: primary artifact hash mismatch')
        if record.get('manifest_sha256')!=sha256_file(manifest_path): raise ValueError(f'{rp}: manifest hash mismatch')
        if editorial.get('sha256')!=sha256_file(decision_path): raise ValueError(f'{rp}: editorial decision hash mismatch')
        decision=json.loads(decision_path.read_text(encoding='utf-8'))
        if decision.get('manifest_sha256')!=record.get('manifest_sha256'): raise ValueError(f'{rp}: editorial decision not bound to published manifest')
        if decision.get('document_id')!=record.get('document_id'): raise ValueError(f'{rp}: editorial decision document mismatch')
        if decision.get('decision')!='accept' or decision.get('pages_approved') is not True:
            raise ValueError(f'{rp}: editorial decision does not authorize Pages publication')
        for key in ('decision_id','decision','pages_approved','reviewer','reviewed_at'):
            if editorial.get(key)!=decision.get(key):
                raise ValueError(f'{rp}: publication record disagrees with editorial decision: {key}')
        meta=json.loads(metadata_path.read_text(encoding='utf-8'))
        did=meta['document_id']
        if did in ids: raise ValueError(f'duplicate document ID: {did}')
        ids.add(did)
        slug=did.replace('.','-')
        studies.append({
            'record_path':rp,'record':record,'packet':packet,'manifest':manifest,'source':source,
            'metadata':meta,'document_id':did,'slug':slug,'commit':commit,
            'decision':decision,'decision_sha256':editorial['sha256'],
        })
    return studies


def _published_source_map(studies: list[dict]) -> dict[Path,dict]:
    return {study['source'].resolve():study for study in studies}


def _declared_media(study: dict) -> dict[Path,str]:
    packet=study['packet'].resolve(); result={}
    for rel in study['manifest']['artifacts']:
        p=(packet/rel).resolve()
        if p.suffix.lower() in MEDIA:
            result[p]=p.name
    return result


def _repo_source_url(commit: str, relative: str, fragment: str='') -> str:
    url=f'https://github.com/{REPO_SLUG}/blob/{commit}/{relative}'
    return url+(f'#{fragment}' if fragment else '')


def _require_html_fragment(candidate: Path, fragment: str, source: Path, original: str) -> None:
    if not fragment or candidate.suffix.lower() not in {'.html','.htm'}:
        return
    soup=BeautifulSoup(candidate.read_text(encoding='utf-8'),'html.parser')
    if soup.find(id=fragment) is None:
        raise ValueError(f'{source}: unresolved internal fragment: {original}')


def _rewrite_links(article, study: dict, root: Path, source_map: dict[Path,dict], base_path: str, target: Path) -> list[dict]:
    rewrites=[]; source=study['source'].resolve(); media=_declared_media(study)
    for tag in article.find_all('a',href=True):
        original=tag['href']
        if original.startswith('#'):
            fragment=original[1:]
            if not fragment or article.find(id=fragment) is None:
                raise ValueError(f'{source}: unresolved internal fragment: {original}')
            rewrites.append({'source_href':original,'projected_href':original,'kind':'local-anchor'})
            continue
        parsed=urlsplit(original)
        if parsed.scheme in {'http','https','mailto','tel'} or original.startswith('//'):
            continue
        if not parsed.path:
            continue
        if parsed.path.startswith('/'):
            candidate=(root/parsed.path.lstrip('/')).resolve()
        else:
            candidate=(source.parent/parsed.path).resolve()
        if not _inside(root,candidate):
            raise ValueError(f'{source}: internal href escapes repository: {original}')
        _require_html_fragment(candidate,parsed.fragment,source,original)
        projected=None; kind=None
        if candidate in source_map:
            other=source_map[candidate]
            projected=site_url(base_path,f"p/{other['slug']}/")
            if parsed.fragment: projected+=f'#{parsed.fragment}'
            kind='cross-publication'
        elif candidate in media:
            name=media[candidate]
            (target/'assets').mkdir(exist_ok=True)
            shutil.copy2(candidate,target/'assets'/name)
            projected='assets/'+name
            if parsed.fragment: projected+=f'#{parsed.fragment}'
            kind='declared-local-asset'
        elif candidate.is_file():
            relative=candidate.relative_to(root).as_posix()
            projected=_repo_source_url(study['commit'],relative,parsed.fragment)
            kind='repository-source-fallback'
        else:
            raise ValueError(f'{source}: unresolved internal href: {original}')
        if parsed.query and projected.startswith(('http://','https://')):
            split=urlsplit(projected)
            projected=urlunsplit((split.scheme,split.netloc,split.path,parsed.query,split.fragment))
        tag['href']=projected
        rewrites.append({'source_href':original,'projected_href':projected,'kind':kind})
    return rewrites


def _rewrite_media(article, study: dict, target: Path) -> list[dict]:
    rewrites=[]; packet=study['packet'].resolve(); allowed=_declared_media(study)
    for tag in article.find_all(src=True):
        original=tag['src']
        parsed=urlsplit(original)
        if parsed.scheme or original.startswith('//') or parsed.path.startswith('/'):
            raise ValueError(f"{study['source']}: non-local asset reference {original}")
        asset=(packet/parsed.path).resolve()
        if asset not in allowed:
            raise ValueError(f"{study['source']}: undeclared asset {original}")
        name=allowed[asset]
        if not asset.is_file(): raise ValueError(f"{study['source']}: missing asset {name}")
        (target/'assets').mkdir(exist_ok=True)
        shutil.copy2(asset,target/'assets'/name)
        projected='assets/'+name
        tag['src']=projected
        rewrites.append({'source_src':original,'projected_src':projected,'kind':'declared-local-asset'})
    return rewrites


def _shell(*,title: str,lang: str,base_path: str,nav: str,body: str,footer: str) -> str:
    css=site_url(base_path,'assets/publisher/signal.css')
    js=site_url(base_path,'assets/publisher/site.js')
    publications=site_url(base_path,'publications/')
    return f'<!doctype html><html lang="{html.escape(lang)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><link rel="stylesheet" href="{css}"></head><body><header class="topbar"><a class="mark" href="{publications}">tare.tools</a> <span class="sub">research reading projection · SIGNAL</span></header><div class="shell"><nav class="nav">{nav}</nav><main class="article">{body}</main></div><footer class="footer">{footer}</footer><script src="{js}" defer></script></body></html>'


def _build_study(study: dict, root: Path, output: Path, source_map: dict[Path,dict], base_path: str, profile: dict) -> dict:
    meta=study['metadata']; source=study['source']; record=study['record']; slug=study['slug']
    target=output/'p'/slug; target.mkdir(parents=True,exist_ok=False)
    source_soup=BeautifulSoup(source.read_text(encoding='utf-8'),'html.parser')
    article=source_soup.select_one('article[data-tare-document]')
    if article is None: raise ValueError(f'{source}: canonical article missing after validation')
    source_fingerprint=semantic_fingerprint(article)
    asset_rewrites=_rewrite_media(article,study,target)
    link_rewrites=_rewrite_links(article,study,root,source_map,base_path,target)
    authority=article.select_one('[data-tare-role="authority-boundary"]')
    if authority: authority['class']=authority.get('class',[])+['authority']
    projected_fingerprint=semantic_fingerprint(article)
    if projected_fingerprint!=source_fingerprint:
        raise ValueError(f'{source}: semantic fingerprint changed during allowed projection transforms')
    publication_index=site_url(base_path,'publications/')
    links=f'<a href="{publication_index}">Publications</a>'+''.join(
        f'<a href="#{x["id"]}">{html.escape(x.get_text(" ",strip=True))}</a>'
        for x in article.find_all(['h2','h3']) if x.get('id')
    )
    decision={**study['decision'],'sha256':study['decision_sha256']}
    instrument=(
        f'<section class="instrument"><span class="status">{html.escape(meta["status"])}</span>'
        f'<br>Canonical SHA-256: <code>{html.escape(record["artifact_sha256"][Path(study["manifest"]["primary_artifact"]).name])}</code>'
        f'<br>Editorial decision: <code>{html.escape(decision["decision_id"])}</code>'
        f'<br>Source: <code>{html.escape(source.relative_to(root).as_posix())}</code>'
        f'<br>Signal source: <code>{profile["source_commit"][:12]}</code></section>'
    )
    page=_shell(
        title=meta['title'],lang=meta['language'],base_path=base_path,nav=links,
        body=instrument+str(article),footer=f'build {study["commit"]} · SIGNAL profile {profile["profile_version"]}',
    )
    (target/'index.html').write_text(page,encoding='utf-8')
    projection={
        'record_version':'1.1','document_id':study['document_id'],'source_path':source.relative_to(root).as_posix(),
        'source_sha256':record['artifact_sha256'][Path(study['manifest']['primary_artifact']).name],
        'build_commit':study['commit'],'base_path':base_path,'signal_profile_sha256':sha256_file(PROFILE),
        'output_path':site_url(base_path,f'p/{slug}/'),'source_semantic_fingerprint':source_fingerprint,
        'projected_semantic_fingerprint':projected_fingerprint,'semantic_parity':source_fingerprint==projected_fingerprint,
        'editorial_decision':decision,'link_rewrites':link_rewrites,'asset_rewrites':asset_rewrites,
        'transformations':['SIGNAL shell added','TOC generated','declared local assets copied','internal hrefs deterministically resolved'],
    }
    (target/'PROJECTION_RECORD.json').write_text(json.dumps(projection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'document_id':study['document_id'],'title':meta['title'],'abstract':meta['abstract'],'status':meta['status'],'url':site_url(base_path,f'p/{slug}/'),'language':meta['language']}


def _parity_report(incumbent: Path | None, output: Path, incumbent_profile: dict | None) -> dict:
    if incumbent is None:
        return {'record_version':'1.0','status':'NOT_APPLICABLE','reason':'no incumbent supplied'}
    missing=[]; modified=[]; unchanged=0
    incumbent_files=[p for p in incumbent.rglob('*') if p.is_file()]
    for src in incumbent_files:
        rel=src.relative_to(incumbent); dst=output/rel
        if not dst.is_file(): missing.append(rel.as_posix()); continue
        if sha256_file(src)!=sha256_file(dst): modified.append(rel.as_posix())
        else: unchanged+=1
    critical=list((incumbent_profile or {}).get('critical_paths',[]))
    critical_missing=[p for p in critical if not (output/p).is_file()]
    additions=sorted(
        p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file() and not (incumbent/p.relative_to(output)).is_file()
    )
    status='PASS' if not missing and not modified and not critical_missing else 'FAIL'
    return {
        'record_version':'1.0','status':status,'incumbent_source_ref':(incumbent_profile or {}).get('source_ref'),
        'incumbent_file_count':len(incumbent_files),'unchanged_incumbent_files':unchanged,'missing_incumbent_paths':missing,
        'modified_incumbent_paths':modified,'critical_paths':critical,'critical_missing':critical_missing,'additive_paths':additions,
    }


def build(root: Path, output: Path, *, base_path: str='/tare.tools.research/', incumbent: Path | None=None) -> list[dict]:
    root=root.resolve(); output=output.resolve(); base_path=normalize_base_path(base_path)
    incumbent=incumbent.resolve() if incumbent else None
    profile=json.loads(PROFILE.read_text(encoding='utf-8'))
    incumbent_profile=json.loads(INCUMBENT_PROFILE.read_text(encoding='utf-8')) if INCUMBENT_PROFILE.is_file() else None
    if incumbent_profile and normalize_base_path(incumbent_profile['base_path'])!=base_path:
        raise ValueError('configured Pages base path disagrees with pinned incumbent profile')
    _copy_tree(incumbent,output)
    publisher_assets=output/'assets'/'publisher'; publisher_assets.mkdir(parents=True,exist_ok=True)
    for name in ('signal.css','site.js'): shutil.copy2(ASSETS/name,publisher_assets/name)
    commit=head(root)
    source_studies=_load_studies(root,commit); source_map=_published_source_map(source_studies)
    studies=[_build_study(s,root,output,source_map,base_path,profile) for s in source_studies]
    cards=''.join(
        f'<article data-study><a href="{x["url"]}">{html.escape(x["title"])}</a><p>{html.escape(x["abstract"])}</p><small>{html.escape(x["status"])} · {html.escape(x["document_id"])}</small></article>'
        for x in studies
    ) or '<p>No editorially approved canonical HTML publication is projected yet.</p>'
    body=f'<section class="instrument"><span class="status">SIGNAL</span><h1>tare.tools research publications</h1><p>Additive, derived reading projections. The stable incumbent remains the root experience until explicit cutover.</p><input data-search aria-label="Search publications" placeholder="Search publications"></section><section>{cards}</section>'
    publication_dir=output/'publications'; publication_dir.mkdir(parents=True,exist_ok=True)
    (publication_dir/'index.html').write_text(_shell(title='tare.tools research publications',lang='en',base_path=base_path,nav=f'<a href="{site_url(base_path)}">Incumbent home</a>',body=body,footer=f'build {commit} · allowlisted publication records only'),encoding='utf-8')
    (publication_dir/'search.json').write_text(json.dumps(studies,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if incumbent is None:
        shutil.copy2(publication_dir/'index.html',output/'index.html')
    parity=_parity_report(incumbent,output,incumbent_profile)
    meta_dir=output/'publication-meta'; meta_dir.mkdir(parents=True,exist_ok=True)
    (meta_dir/'PARITY_REPORT.json').write_text(json.dumps(parity,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if parity['status']=='FAIL': raise ValueError('incumbent parity failed: '+json.dumps(parity,ensure_ascii=False))
    return studies


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=ROOT); ap.add_argument('--output',type=Path,default=ROOT/'site'/'_site'); ap.add_argument('--base-path',default=os.environ.get('PAGES_BASE_PATH','/tare.tools.research/')); ap.add_argument('--incumbent',type=Path); args=ap.parse_args()
    studies=build(args.root,args.output,base_path=args.base_path,incumbent=args.incumbent)
    print(f'PASS Pages shadow build studies={len(studies)} output={args.output} base_path={normalize_base_path(args.base_path)} incumbent={args.incumbent}')
