#!/usr/bin/env python3
"""Validate the tare-research-html/1.0 publication profile."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re


REQUIRED_SECTIONS={"scope","evidence","findings","limitations","references"}
ACTIVE_TAGS={"form","iframe","script"}


class ProfileParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors=[]; self.ids=[]; self.tags=[]; self.roles=set(); self.article=False
        self.has_title=False; self.has_main=False; self.has_h1=False; self.has_abstract=False
        self.lang=None

    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs); self.tags.append(tag)
        if tag in ACTIVE_TAGS: self.errors.append(f"active element not allowed: {tag}")
        if tag=='html': self.lang=attrs.get('lang')
        if tag=='title': self.has_title=True
        if tag=='main': self.has_main=True
        if tag=='article' and 'data-tare-document' in attrs: self.article=True
        if tag=='h1': self.has_h1=True
        if attrs.get('data-tare-role')=='abstract': self.has_abstract=True
        if attrs.get('data-tare-role'): self.roles.add(attrs['data-tare-role'])
        if attrs.get('data-tare-section'): self.roles.add(attrs['data-tare-section'])
        if attrs.get('id'): self.ids.append(attrs['id'])
        if tag=='img' and not attrs.get('alt'): self.errors.append('image missing alt text')
        if tag in {'img','source','video','audio','object','embed','link'}:
            value=attrs.get('src') or attrs.get('href')
            if value and re.match(r'(?i)https?://|//',value): self.errors.append(f"remote asset not allowed: {value}")
        if any(name.lower().startswith('on') for name in attrs): self.errors.append(f"event handler not allowed: {tag}")


def validate_packet(packet: Path, manifest: dict) -> list[str]:
    errors=[]; primary=packet/manifest['primary_artifact']; metadata_path=packet/'document-metadata.json'
    if not primary.is_file(): return [f"primary artifact missing: {manifest['primary_artifact']}"]
    if not metadata_path.is_file(): return ['document-metadata.json missing']
    try: metadata=json.loads(metadata_path.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError) as exc: return [f'document metadata invalid: {exc}']
    for key in ('document_id','document_type','status'):
        if metadata.get(key)!=manifest.get(key): errors.append(f'metadata {key} disagrees with manifest')
    if not isinstance(metadata.get('language'),str) or not metadata['language']: errors.append('metadata language required')
    if not isinstance(metadata.get('abstract'),str) or not metadata['abstract']: errors.append('metadata abstract required')
    if not isinstance(metadata.get('authors'),list) or not metadata['authors']: errors.append('metadata authors required')
    raw=primary.read_text(encoding='utf-8')
    if not re.match(r'\s*<!doctype html\b',raw,re.I): errors.append('HTML5 doctype required')
    parser=ProfileParser(); parser.feed(raw); errors.extend(parser.errors)
    if not parser.lang: errors.append('html lang required')
    elif parser.lang!=metadata.get('language'): errors.append('HTML lang disagrees with metadata language')
    for ok,name in ((parser.has_title,'title'),(parser.has_main,'main'),(parser.article,'article[data-tare-document]'),(parser.has_h1,'h1'),(parser.has_abstract,'abstract')):
        if not ok: errors.append(f'HTML {name} required')
    for role in REQUIRED_SECTIONS|{'document-header','authority-boundary'}:
        if role not in parser.roles: errors.append(f'HTML role/section required: {role}')
    duplicates={x for x in parser.ids if parser.ids.count(x)>1}
    if duplicates: errors.append(f'duplicate IDs: {sorted(duplicates)}')
    return errors


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('manifest',type=Path); args=ap.parse_args()
    manifest=json.loads(args.manifest.read_text(encoding='utf-8'))
    errors=validate_packet(args.manifest.parent,manifest)
    print('PASS canonical HTML' if not errors else '\n'.join('ERROR '+x for x in errors))
    raise SystemExit(bool(errors))
