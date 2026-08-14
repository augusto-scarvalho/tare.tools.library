#!/usr/bin/env python3
"""Validate the tare-research-html/1.0 publication profile.

The validator enforces the DOM relationships promised by the publication
standard; element presence in unrelated parts of a document is not sufficient.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from bs4 import BeautifulSoup, Doctype

REQUIRED_SECTIONS=("scope","evidence","findings","limitations","references")
ACTIVE_TAGS={"form","iframe","script"}
REMOTE_RE=re.compile(r"(?i)^(?:https?:)?//")


def _norm(value: str) -> str:
    return " ".join(value.split())


def _validate_metadata(metadata: dict, manifest: dict) -> list[str]:
    errors=[]
    for key in ("document_id","document_type","status"):
        if metadata.get(key)!=manifest.get(key): errors.append(f"metadata {key} disagrees with manifest")
    for key in ("title","created_at","language","abstract"):
        if not isinstance(metadata.get(key),str) or not metadata[key].strip(): errors.append(f"metadata {key} required")
    if not isinstance(metadata.get("authors"),list) or not metadata["authors"]:
        errors.append("metadata authors required")
    else:
        for i,author in enumerate(metadata["authors"]):
            if not isinstance(author,dict) or not isinstance(author.get("name"),str) or not author.get("name"):
                errors.append(f"metadata authors[{i}].name required")
            if not isinstance(author,dict) or author.get("role") not in {"author","editor","contributor","agent"}:
                errors.append(f"metadata authors[{i}].role invalid")
    if not isinstance(metadata.get("bounded_contexts"),list) or not metadata["bounded_contexts"]:
        errors.append("metadata bounded_contexts required")
    if not isinstance(metadata.get("provenance"),dict) or not metadata["provenance"].get("origin"):
        errors.append("metadata provenance.origin required")
    return errors


def _validate_dom(raw: str, metadata: dict) -> list[str]:
    errors=[]
    if not re.match(r"\s*<!doctype html\b",raw,re.I): errors.append("HTML5 doctype required")
    soup=BeautifulSoup(raw,"html.parser")
    doctypes=[x for x in soup.contents if isinstance(x,Doctype)]
    if not doctypes: errors.append("HTML doctype node required")

    html=soup.find("html")
    if html is None:
        errors.append("HTML html element required")
        return errors
    lang=html.get("lang")
    if not lang: errors.append("html lang required")
    elif lang!=metadata.get("language"): errors.append("HTML lang disagrees with metadata language")

    title=soup.find("title")
    if title is None or not title.get_text(strip=True): errors.append("HTML title required")

    mains=soup.find_all("main")
    if len(mains)!=1:
        errors.append(f"exactly one main required (found {len(mains)})")
        main=mains[0] if mains else None
    else:
        main=mains[0]

    article=None
    if main is not None:
        direct=main.find_all("article",attrs={"data-tare-document":True},recursive=False)
        if len(direct)!=1:
            errors.append(f"main > article[data-tare-document] required exactly once (found {len(direct)})")
        else:
            article=direct[0]
    all_articles=soup.find_all("article",attrs={"data-tare-document":True})
    if len(all_articles)!=1: errors.append(f"exactly one article[data-tare-document] required (found {len(all_articles)})")

    ids=[]
    for tag in soup.find_all(True):
        if tag.name in ACTIVE_TAGS: errors.append(f"active element not allowed: {tag.name}")
        if tag.get("id"): ids.append(tag["id"])
        if any(str(name).lower().startswith("on") for name in tag.attrs): errors.append(f"event handler not allowed: {tag.name}")
        if tag.name in {"img","source","video","audio","object","embed","link"}:
            value=tag.get("src") or tag.get("href")
            if value and REMOTE_RE.match(value): errors.append(f"remote asset not allowed: {value}")
        if tag.name=="img" and not tag.get("alt"): errors.append("image missing alt text")
        if tag.name=="figure" and tag.find("figcaption") is None: errors.append("figure missing figcaption")
        if tag.name=="table" and tag.find("caption",recursive=False) is None and not tag.get("aria-label"):
            errors.append("table requires caption or aria-label")
    duplicates=sorted({x for x in ids if ids.count(x)>1})
    if duplicates: errors.append(f"duplicate IDs: {duplicates}")

    if article is None: return errors

    header=article.find(attrs={"data-tare-role":"document-header"})
    if header is None: errors.append("HTML role/section required: document-header")
    h1=header.find("h1") if header else None
    if h1 is None: errors.append("HTML h1 required inside document header")
    elif metadata.get("title") and _norm(h1.get_text(" ",strip=True))!=_norm(metadata["title"]):
        errors.append("HTML h1 disagrees with metadata title")
    abstract=header.find(attrs={"data-tare-role":"abstract"}) if header else None
    if abstract is None: errors.append("HTML abstract required inside document header")
    elif metadata.get("abstract") and _norm(abstract.get_text(" ",strip=True))!=_norm(metadata["abstract"]):
        errors.append("HTML abstract disagrees with metadata abstract")

    if article.find(attrs={"data-tare-role":"authority-boundary"}) is None:
        errors.append("HTML role/section required: authority-boundary")

    for role in REQUIRED_SECTIONS:
        matches=article.find_all("section",attrs={"data-tare-section":role})
        if len(matches)!=1:
            errors.append(f"HTML role/section required exactly once: {role}")
            continue
        if matches[0].get("id")!=role:
            errors.append(f"HTML section {role} must use stable id={role}")

    return errors


def validate_artifacts(packet: Path, manifest: dict, primary_name: str, metadata_name: str) -> list[str]:
    errors=[]
    if not isinstance(primary_name,str): return ["primary_artifact required"]
    primary=packet/primary_name; metadata_path=packet/metadata_name
    if not primary.is_file(): return [f"primary artifact missing: {primary_name}"]
    if not metadata_path.is_file(): return ["document-metadata.json missing"]
    try: metadata=json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: return [f"document metadata invalid: {exc}"]
    errors.extend(_validate_metadata(metadata,manifest))
    try: raw=primary.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc: return errors+[f"primary artifact must be UTF-8: {exc}"]
    errors.extend(_validate_dom(raw,metadata))
    return errors


def validate_packet(packet: Path, manifest: dict) -> list[str]:
    return validate_artifacts(packet, manifest, manifest.get("primary_artifact"), "document-metadata.json")


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("manifest",type=Path); args=ap.parse_args()
    manifest=json.loads(args.manifest.read_text(encoding="utf-8"))
    errors=validate_packet(args.manifest.parent,manifest)
    print("PASS canonical HTML" if not errors else "\n".join("ERROR "+x for x in errors))
    raise SystemExit(bool(errors))
