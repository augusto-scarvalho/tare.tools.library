#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSERTIONS = ROOT / "catalog" / "IDENTITY_ASSERTIONS.json"
REF_ROOT = ROOT / "corpus" / "library-references"
OUT_MD = ROOT / "catalog" / "IDENTITY_ASSERTIONS.md"


def refs_by_id():
    out = {}
    for p in REF_ROOT.rglob("*.reference.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        out[d["file_library_id"]] = (p, d)
    return out


def main():
    src = json.loads(ASSERTIONS.read_text(encoding="utf-8"))
    refs = refs_by_id()
    rows=[]
    for a in src["assertions"]:
        fid=a["target_file_library_id"]
        if fid not in refs:
            raise SystemExit(f"missing target reference: {fid}")
        p,d=refs[fid]
        if d["title"] != a["target_title"]:
            raise SystemExit(f"title mismatch for {fid}")
        existing=d.get("reported_sha256")
        if existing and existing != a["reported_sha256"]:
            raise SystemExit(f"conflicting reported hash for {fid}")
        d["reported_sha256"]=a["reported_sha256"]
        d["reported_size_bytes"]=a["reported_size_bytes"]
        d["hash_status"]="REPORTED_NOT_LOCALLY_VERIFIED"
        note=(d.get("notes") or "").strip()
        evidence=f"Identity asserted by File Library manifest {a['assertion_source_title']} ({a['assertion_source_file_library_id']}); manifest bytes not locally materialized."
        if evidence not in note:
            d["notes"]=(note+" " + evidence).strip()
        p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        rows.append((d["title"],fid,a["reported_sha256"],a["reported_size_bytes"],a["assertion_source_title"],a["assertion_source_file_library_id"]))
    md=["# Expected Identity Assertions","","> These SHA-256/size values are reported by separate validation manifests found in the File Library. They are identity constraints for future exact-byte rehydration, **not locally verified source hashes yet**.","", "| Target | File Library ID | Expected SHA-256 | Bytes | Assertion source |", "|---|---|---|---:|---|"]
    for title,fid,h,size,st,sid in rows:
        md.append(f"| `{title}` | `{fid}` | `{h}` | {size} | `{st}` (`{sid}`) |")
    OUT_MD.write_text("\n".join(md)+"\n",encoding="utf-8")
    print(f"PASS identity assertions applied: {len(rows)}")

if __name__=="__main__": main()
