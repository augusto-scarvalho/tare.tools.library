#!/usr/bin/env python3
"""Stdlib-only repository gate for tare-research-html/1.0 packets."""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re

REQUIRED=("scope","evidence","findings","limitations","references")


class ContractParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.errors=[]; self.ids=[]
        self.lang=None; self.html=0; self.main=0; self.article=0; self.direct_article=0
        self.article_depth=None; self.header_depth=None
        self.title=0; self.title_text=[]; self.capture_title=False
        self.h1=0; self.h1_text=[]; self.capture_h1=False
        self.abstract=0; self.abstract_text=[]; self.abstract_depth=None
        self.authority=0; self.sections={key:[] for key in REQUIRED}; self.doctype=False

    def handle_decl(self,decl):
        if decl.strip().lower()=='doctype html': self.doctype=True

    def handle_starttag(self,tag,attrs_list):
        attrs=dict(attrs_list); parent=self.stack[-1] if self.stack else None; depth=len(self.stack)+1
        if attrs.get('id'): self.ids.append(attrs['id'])
        if tag=='html': self.html+=1; self.lang=self.lang or attrs.get('lang')
        if tag=='title': self.title+=1; self.capture_title=True
        if tag=='main': self.main+=1
        if tag=='article' and 'data-tare-document' in attrs:
            self.article+=1
            if parent=='main':
                self.direct_article+=1
                if self.article_depth is None: self.article_depth=depth
        inside=self.article_depth is not None and depth>=self.article_depth
        if inside:
            role=attrs.get('data-tare-role'); section=attrs.get('data-tare-section')
            if role=='document-header': self.header_depth=depth
            elif role=='authority-boundary': self.authority+=1
            elif role=='abstract': self.abstract+=1; self.abstract_depth=depth; self.capture_abstract=True
            if section in self.sections: self.sections[section].append(attrs.get('id'))
            if tag=='h1' and self.header_depth is not None and depth>self.header_depth:
                self.h1+=1; self.capture_h1=True
        self.stack.append(tag)

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs); self.handle_endtag(tag)

    def handle_endtag(self,tag):
        depth=len(self.stack)
        if tag=='title': self.capture_title=False
        if tag=='h1': self.capture_h1=False
        if self.abstract_depth==depth: self.capture_abstract=False; self.abstract_depth=None
        if self.header_depth==depth: self.header_depth=None
        if self.article_depth==depth and tag=='article': self.article_depth=None
        if self.stack and self.stack[-1]==tag: self.stack.pop()
        elif tag in self.stack:
            self.errors.append(f'malformed nesting near closing tag: {tag}')
            idx=len(self.stack)-1-self.stack[::-1].index(tag); self.stack=self.stack[:idx]
        else: self.errors.append(f'closing tag without opener: {tag}')

    def handle_data(self,data):
        if self.capture_title: self.title_text.append(data)
        if self.capture_h1: self.h1_text.append(data)
        if self.capture_abstract: self.abstract_text.append(data)


def norm(value): return ' '.join(value.split())


def validate_packet(packet: Path,manifest: dict) -> list[str]:
    errors=[]; primary_name=manifest.get('primary_artifact')
    if not isinstance(primary_name,str): return ['primary_artifact required']
    primary=packet/primary_name; metadata_path=packet/'document-metadata.json'
    if not primary.is_file(): return [f'primary artifact missing: {primary_name}']
    if not metadata_path.is_file(): return ['document-metadata.json missing']
    try: meta=json.loads(metadata_path.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError) as exc: return [f'document metadata invalid: {exc}']
    for key in ('document_id','document_type','status'):
        if meta.get(key)!=manifest.get(key): errors.append(f'metadata {key} disagrees with manifest')
    for key in ('title','created_at','language','abstract'):
        if not isinstance(meta.get(key),str) or not meta[key].strip(): errors.append(f'metadata {key} required')
    if not isinstance(meta.get('authors'),list) or not meta['authors']: errors.append('metadata authors required')
    if not isinstance(meta.get('bounded_contexts'),list) or not meta['bounded_contexts']: errors.append('metadata bounded_contexts required')
    if not isinstance(meta.get('provenance'),dict) or not meta['provenance'].get('origin'): errors.append('metadata provenance.origin required')
    raw=primary.read_text(encoding='utf-8')
    if not re.match(r'\s*<!doctype html\b',raw,re.I): errors.append('HTML5 doctype required')
    parser=ContractParser(); parser.feed(raw); parser.close(); errors.extend(parser.errors)
    if not parser.doctype: errors.append('HTML doctype node required')
    if parser.html!=1: errors.append(f'exactly one html required (found {parser.html})')
    if not parser.lang: errors.append('html lang required')
    elif parser.lang!=meta.get('language'): errors.append('HTML lang disagrees with metadata language')
    if parser.title!=1 or not norm(''.join(parser.title_text)): errors.append('HTML title required exactly once')
    if parser.main!=1: errors.append(f'exactly one main required (found {parser.main})')
    if parser.article!=1: errors.append(f'exactly one article[data-tare-document] required (found {parser.article})')
    if parser.direct_article!=1: errors.append(f'main > article[data-tare-document] required exactly once (found {parser.direct_article})')
    duplicates=sorted({x for x in parser.ids if parser.ids.count(x)>1})
    if duplicates: errors.append(f'duplicate IDs: {duplicates}')
    if parser.h1!=1: errors.append('HTML h1 required exactly once inside document header')
    elif norm(''.join(parser.h1_text))!=norm(meta.get('title','')): errors.append('HTML h1 disagrees with metadata title')
    if parser.abstract!=1: errors.append('HTML abstract required exactly once inside document header')
    elif norm(''.join(parser.abstract_text))!=norm(meta.get('abstract','')): errors.append('HTML abstract disagrees with metadata abstract')
    if parser.authority!=1: errors.append('HTML role/section required exactly once: authority-boundary')
    for key in REQUIRED:
        values=parser.sections[key]
        if len(values)!=1: errors.append(f'HTML role/section required exactly once: {key}')
        elif values[0]!=key: errors.append(f'HTML section {key} must use stable id={key}')
    return errors
