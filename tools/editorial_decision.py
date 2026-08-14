#!/usr/bin/env python3
"""Create the maintainer-owned v1.1 editorial decision sidecar."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'/'publisher'/'src'))
from tare_tools_publisher.git_backend import _packet_hash
from tare_tools_publisher.policy import validate
from tare_tools_publisher.translation import file_hash, validate_pages_translation


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('packet',type=Path); ap.add_argument('--decision-id',required=True)
    ap.add_argument('--submission-repository',required=True); ap.add_argument('--submission-pr',required=True,type=int)
    ap.add_argument('--submission-head-sha',required=True); ap.add_argument('--submission-author',required=True)
    ap.add_argument('--reviewer',required=True); ap.add_argument('--reviewer-name',required=True)
    ap.add_argument('--pages-approved',action='store_true'); ap.add_argument('--reviewed-at',required=True); ap.add_argument('--notes',default='')
    args=ap.parse_args(); packet=args.packet.resolve()
    manifest=json.loads(packet.joinpath('PUBLISH_MANIFEST.json').read_text(encoding='utf-8'))
    errors=validate(manifest)
    translation_errors,_=validate_pages_translation(packet,manifest)
    if errors or translation_errors: raise SystemExit('DENY '+ '; '.join(errors+translation_errors))
    if args.reviewer == args.submission_author: raise SystemExit('DENY submitter cannot approve their own editorial decision')
    if args.pages_approved and 'pages' not in manifest.get('requested_channels',[]): raise SystemExit('DENY Pages was not requested')
    decision={
        'decision_version':'1.1','decision_id':args.decision_id,'document_id':manifest['document_id'],
        'manifest_sha256':file_hash(packet/'PUBLISH_MANIFEST.json'),'packet_sha256':_packet_hash(packet/'PUBLISH_MANIFEST.json',manifest),
        'submission':{'repository':args.submission_repository,'pr_number':args.submission_pr,'head_sha':args.submission_head_sha,'author_login':args.submission_author},
        'decision':'accept','pages_approved':args.pages_approved,
        'reviewer':{'name':args.reviewer_name,'role':'editorial-reviewer','identity_ref':f'github:{args.reviewer}'},
        'reviewed_at':args.reviewed_at,'notes':args.notes,
    }
    (packet/'EDITORIAL_DECISION.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'WROTE {packet / "EDITORIAL_DECISION.json"}')
    return 0


if __name__=='__main__': raise SystemExit(main())
