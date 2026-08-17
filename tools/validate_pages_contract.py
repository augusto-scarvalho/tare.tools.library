#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from pages_common import normalize_base_path, semantic_fingerprint, sha256_file


def _resolve_site_target(output: Path, page: Path, value: str, base_path: str) -> Path | None:
    if not value:
        return None
    parsed=urlsplit(value)
    if parsed.scheme in {'http','https','mailto','tel'} or value.startswith('//'):
        return None
    path=parsed.path
    if not path:
        return page if parsed.fragment else None
    if path.startswith('/'):
        if not path.startswith(base_path):
            raise ValueError(f'URL outside Pages base path: {value}')
        target=output/path[len(base_path):]
    else:
        target=(page.parent/path).resolve()
        target.relative_to(output.resolve())
    if path.endswith('/') or target.is_dir():
        target=target/'index.html'
    return target


def _fragment_exists(target: Path, fragment: str) -> bool:
    if not fragment or target.suffix.lower() not in {'.html','.htm'}:
        return True
    soup=BeautifulSoup(target.read_text(encoding='utf-8'),'html.parser')
    return soup.find(id=fragment) is not None


def validate(output: Path, root: Path, incumbent: Path, base_path: str) -> list[str]:
    output=output.resolve(); root=root.resolve(); incumbent=incumbent.resolve(); base_path=normalize_base_path(base_path)
    errors=[]
    report_path=output/'publication-meta'/'PARITY_REPORT.json'
    if not report_path.is_file():
        errors.append('missing PARITY_REPORT.json')
    else:
        report=json.loads(report_path.read_text(encoding='utf-8'))
        if report.get('status')!='PASS': errors.append('incumbent parity report is not PASS')
    for source in incumbent.rglob('*'):
        if not source.is_file(): continue
        relative=source.relative_to(incumbent); projected=output/relative
        if not projected.is_file(): errors.append(f'incumbent path missing: {relative.as_posix()}')
        elif sha256_file(source)!=sha256_file(projected): errors.append(f'incumbent path modified: {relative.as_posix()}')
    for page in [output/'publications'/'index.html',*sorted(output.glob('p/*/index.html'))]:
        if not page.is_file(): errors.append(f'missing generated page: {page.relative_to(output)}'); continue
        soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
        for node in soup.find_all(['a','link'],href=True):
            try: target=_resolve_site_target(output,page,node['href'],base_path)
            except ValueError as exc: errors.append(f'{page}: {exc}'); continue
            if target is not None and not target.is_file(): errors.append(f'{page}: broken href {node["href"]}')
            elif target is not None and not _fragment_exists(target,urlsplit(node['href']).fragment): errors.append(f'{page}: broken fragment {node["href"]}')
        for node in soup.find_all(src=True):
            try: target=_resolve_site_target(output,page,node['src'],base_path)
            except ValueError as exc: errors.append(f'{page}: {exc}'); continue
            if target is not None and not target.is_file(): errors.append(f'{page}: broken src {node["src"]}')
    for page in sorted(output.glob('p/*/index.html')):
        record_path=page.parent/'PROJECTION_RECORD.json'
        if not record_path.is_file(): errors.append(f'{page}: missing PROJECTION_RECORD.json'); continue
        record=json.loads(record_path.read_text(encoding='utf-8'))
        if record.get('base_path')!=base_path: errors.append(f'{record_path}: base path mismatch')
        if record.get('semantic_parity') is not True: errors.append(f'{record_path}: semantic parity not proven')
        if record.get('source_semantic_fingerprint')!=record.get('projected_semantic_fingerprint'): errors.append(f'{record_path}: semantic fingerprints differ')
        article=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser').find('article',attrs={'data-tare-document':True})
        if article is None: errors.append(f'{page}: canonical article missing'); continue
        if semantic_fingerprint(article)!=record.get('projected_semantic_fingerprint'): errors.append(f'{record_path}: final projection fingerprint mismatch')
        source=root/record.get('source_path','')
        if not source.is_file(): errors.append(f'{record_path}: source path missing'); continue
        if sha256_file(source)!=record.get('source_sha256'): errors.append(f'{record_path}: source SHA mismatch')
        source_article=BeautifulSoup(source.read_text(encoding='utf-8'),'html.parser').find('article',attrs={'data-tare-document':True})
        if source_article is None or semantic_fingerprint(source_article)!=record.get('source_semantic_fingerprint'): errors.append(f'{record_path}: source fingerprint mismatch')
        editorial=record.get('editorial_decision')
        if not isinstance(editorial,dict) or editorial.get('decision')!='accept' or editorial.get('pages_approved') is not True or not editorial.get('sha256'): errors.append(f'{record_path}: editorial approval evidence missing')
        else:
            decision_path=source.parent/'EDITORIAL_DECISION.json'
            if not decision_path.is_file(): errors.append(f'{record_path}: editorial decision source missing')
            else:
                decision=json.loads(decision_path.read_text(encoding='utf-8'))
                if sha256_file(decision_path)!=editorial['sha256']: errors.append(f'{record_path}: editorial decision SHA mismatch')
                if decision.get('decision')!='accept' or decision.get('pages_approved') is not True: errors.append(f'{record_path}: editorial decision does not authorize Pages publication')
                for key in ('decision_id','document_id','manifest_sha256','decision','pages_approved','reviewer','reviewed_at'):
                    if editorial.get(key)!=decision.get(key): errors.append(f'{record_path}: projected editorial decision mismatch: {key}')
        meta_artifact_name = record.get('pages_projection', {}).get('metadata_artifact', 'document-metadata.json') if isinstance(record.get('pages_projection'), dict) else 'document-metadata.json'
        metadata=json.loads((source.parent / meta_artifact_name).read_text(encoding='utf-8'))
        soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
        if soup.html is None or soup.html.get('lang')!=metadata.get('language'): errors.append(f'{page}: projection language mismatch')
    return errors


if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('output',type=Path); ap.add_argument('--root',type=Path,required=True); ap.add_argument('--incumbent',type=Path,required=True); ap.add_argument('--base-path',default='/tare.tools.research/'); args=ap.parse_args()
    errors=validate(args.output,args.root,args.incumbent,args.base_path)
    print('PASS Pages contract validation' if not errors else '\n'.join('ERROR '+x for x in errors))
    raise SystemExit(bool(errors))
