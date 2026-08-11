#!/usr/bin/env python3
from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]
files=sorted((ROOT/'corpus'/'library-references').rglob('*.reference.json'))
seen=set(); errors=[]
for p in files:
    try: d=json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'{p}: invalid JSON: {e}'); continue
    fid=d.get('file_library_id')
    if not isinstance(fid,str) or not re.fullmatch(r'file_[0-9a-f]+',fid): errors.append(f'{p}: invalid file_library_id')
    if fid in seen: errors.append(f'{p}: duplicate file_library_id {fid}')
    seen.add(fid)
    if d.get('availability')!='LIBRARY_REFERENCE_ONLY': errors.append(f'{p}: availability must be LIBRARY_REFERENCE_ONLY')
    if d.get('materialized_bytes') is not False: errors.append(f'{p}: reference-only record cannot claim materialized bytes')
    if 'source_path' in d: errors.append(f'{p}: must not invent source_path for File Library reference')
    sha=d.get('reported_sha256')
    if sha is not None and not re.fullmatch(r'[0-9a-f]{64}',sha): errors.append(f'{p}: bad reported_sha256')
    if sha and d.get('hash_status')!='REPORTED_NOT_LOCALLY_VERIFIED': errors.append(f'{p}: reported hash must remain unverified')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'library references: {len(files)}/{len(files)} PASS')
