from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse


SEMANTIC_SURFACE_VERSION = "1.1"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_base_path(value: str) -> str:
    value=(value or "/").strip()
    if "://" in value or "?" in value or "#" in value:
        raise ValueError(f"invalid Pages base path: {value!r}")
    parts=PurePosixPath("/"+value.strip("/")).parts
    if ".." in parts:
        raise ValueError(f"invalid Pages base path: {value!r}")
    if value.strip("/")=="":
        return "/"
    return "/"+value.strip("/")+"/"


def site_url(base_path: str, relative: str="") -> str:
    base=normalize_base_path(base_path)
    rel=relative.lstrip("/")
    return base+rel if rel else base


def _asset_name(value: str | None) -> str | None:
    if not value:
        return None
    parsed=urlparse(value)
    return Path(parsed.path).name or parsed.path or value


def semantic_payload(node) -> dict:
    """Return the normalized semantic surface protected by Pages parity.

    This is intentionally narrower than full DOM equivalence. Navigational href
    destinations are excluded because rewrites are independently evidenced and
    validated. The surface does preserve meaning-bearing text plus common HTML
    structure so same-text structural regressions do not silently false-green.
    """
    return {
        "semantic_surface_version": SEMANTIC_SURFACE_VERSION,
        "text": node.get_text(" ",strip=True),
        "ids": [x["id"] for x in node.find_all(id=True)],
        "headings": [
            (x.name,x.get("id"),x.get_text(" ",strip=True))
            for x in node.find_all(["h1","h2","h3","h4","h5","h6"])
        ],
        "roles": [
            (x.name,x.get("data-tare-role"),x.get("data-tare-section"),x.get("id"))
            for x in node.find_all(True)
            if x.get("data-tare-role") or x.get("data-tare-section")
        ],
        "paragraphs": [
            (x.get("id"),x.get_text(" ",strip=True)) for x in node.find_all("p")
        ],
        "lists": [
            (x.name,x.get("id"),x.get_text(" ",strip=True)) for x in node.find_all(["ul","ol"])
        ],
        "list_items": [x.get_text(" ",strip=True) for x in node.find_all("li")],
        "blockquotes": [x.get_text(" ",strip=True) for x in node.find_all("blockquote")],
        "emphasis": [
            (x.name,x.get_text(" ",strip=True)) for x in node.find_all(["em","strong"])
        ],
        "details": [
            (x.get("id"),x.get_text(" ",strip=True)) for x in node.find_all("details")
        ],
        "summaries": [x.get_text(" ",strip=True) for x in node.find_all("summary")],
        "figures": [x.get_text(" ",strip=True) for x in node.find_all("figure")],
        "tables": [x.get_text(" ",strip=True) for x in node.find_all("table")],
        "links": [x.get_text(" ",strip=True) for x in node.find_all("a",href=True)],
        "images": [(x.get("alt",""),_asset_name(x.get("src"))) for x in node.find_all("img")],
        "code": [x.get_text("\n",strip=False) for x in node.find_all(["code","pre"])],
    }


def semantic_fingerprint(node) -> str:
    payload=semantic_payload(node)
    return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
