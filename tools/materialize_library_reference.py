#!/usr/bin/env python3
"""Materialize exact bytes for a File Library discovery reference.

This command never reconstructs content from snippets. It requires a caller-supplied
exact-byte file and records how that file was acquired. Reference sidecars remain
immutable discovery evidence; materialization is represented by a separate crosswalk.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT_DEFAULT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def safe_name(name: str) -> str:
    # Keep the visible original name while removing path separators/control chars.
    name = name.replace('\\', '_').replace('/', '_').strip()
    name = re.sub(r'[\x00-\x1f]', '_', name)
    return name or 'artifact.bin'


def find_existing_by_hash(root: Path, sha: str) -> tuple[dict, Path] | None:
    for p in sorted((root / 'corpus' / 'manifests').glob('*.json')):
        try:
            m = load(p)
        except (json.JSONDecodeError, OSError):
            continue
        if m.get('provenance', {}).get('source_sha256') == sha:
            source = root / m.get('provenance', {}).get('source_path', '')
            if source.is_file() and digest(source) == sha:
                return m, source
    return None


def translation_exists(root: Path, source_path: Path, source_sha: str) -> bool:
    for p in sorted((root / 'corpus' / 'manifests' / 'translations' / 'en').glob('*.json')):
        try:
            m = load(p)
        except (json.JSONDecodeError, OSError):
            continue
        if m.get('source_sha256') == source_sha and (root / m.get('source_path', '')).resolve() == source_path.resolve():
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--reference', required=True)
    ap.add_argument('--source', required=True)
    ap.add_argument('--root', default=str(ROOT_DEFAULT))
    ap.add_argument('--document-id', required=True)
    ap.add_argument('--title')
    ap.add_argument('--document-type', required=True, choices=['research','proposal','experiment','archaeology','handoff','source','finding'])
    ap.add_argument('--status', required=True, choices=['RESEARCH','PROPOSED','EXPERIMENTAL','HISTORICAL'])
    ap.add_argument('--context', action='append')
    ap.add_argument('--source-language')
    ap.add_argument('--batch', default='file-library-materialized')
    ap.add_argument('--materialization-basis', required=True, choices=['FILE_LIBRARY_EXACT_EXPORT','USER_SUPPLIED_EXACT_EXPORT','OTHER_EXACT_BYTE_SOURCE'])
    args = ap.parse_args()

    root = Path(args.root).resolve()
    reference_path = Path(args.reference).resolve()
    source = Path(args.source).resolve()
    if not reference_path.is_file() or not source.is_file():
        print('DENY reference/source missing')
        return 2
    ref = load(reference_path)
    if ref.get('availability') != 'LIBRARY_REFERENCE_ONLY' or ref.get('materialized_bytes') is not False:
        print('DENY reference is not immutable reference-only record')
        return 2
    sha = digest(source)
    reported = ref.get('reported_sha256')
    if reported and reported != sha:
        print('DENY REPORTED_SHA256_MISMATCH', reported, sha)
        return 3

    cross_dir = root / 'catalog' / 'identity-crosswalk'
    cross_dir.mkdir(parents=True, exist_ok=True)
    cross_path = cross_dir / f"{ref['file_library_id']}.json"
    if cross_path.exists():
        old = load(cross_path)
        if old.get('source_sha256') == sha:
            print('PASS ALREADY_CROSSWALKED', cross_path)
            return 0
        print('DENY crosswalk collision', cross_path)
        return 4

    source_language = args.source_language or ref.get('native_language') or 'unknown'
    contexts = args.context or ref.get('suggested_contexts') or []
    if not contexts:
        print('DENY at least one context required')
        return 2

    existing = find_existing_by_hash(root, sha)
    if existing:
        manifest, materialized_source = existing
        document_id = manifest['document_id']
        status = 'ALREADY_MATERIALIZED_BY_HASH'
        source_rel = materialized_source.relative_to(root).as_posix()
    else:
        original_filename = safe_name(ref.get('title') or source.name)
        # Preserve extension from the actual exact-byte source if the title lacks one.
        if not Path(original_filename).suffix and source.suffix:
            original_filename += source.suffix
        unique_name = f"{ref['file_library_id']}__{original_filename}"
        target_dir = root / 'corpus' / 'original' / args.batch
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / unique_name
        if target.exists():
            print('DENY target collision', target)
            return 4
        shutil.copy2(source, target)
        if digest(target) != sha:
            target.unlink(missing_ok=True)
            print('DENY copy hash mismatch')
            return 5
        source_rel = target.relative_to(root).as_posix()
        document_id = args.document_id
        manifest = {
            'document_id': document_id,
            'title': args.title or ref['title'],
            'document_type': args.document_type,
            'status': args.status,
            'created_at': datetime.now(timezone.utc).date().isoformat(),
            'source_language': source_language,
            'architecture_epoch': None,
            'canonical_commit': None,
            'bounded_contexts': contexts,
            'lineage': {'supersedes': [], 'superseded_by': [], 'derived_from': []},
            'provenance': {
                'origin': 'file-library-exact-materialization',
                'project': 'tare.tools',
                'source_path': source_rel,
                'source_sha256': sha,
                'size_bytes': target.stat().st_size,
                'original_filename': ref['title'],
                'file_library_id': ref['file_library_id'],
                'reference_id': ref['reference_id'],
                'materialization_basis': args.materialization_basis,
                'notes': 'Exact-byte materialization of a prior File Library discovery reference; discovery reference is preserved separately.'
            }
        }
        manifest_path = root / 'corpus' / 'manifests' / f'{unique_name}.json'
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        status = 'MATERIALIZED_NEW'
        materialized_source = target

    if source_language.lower() in {'en','en-us','en-gb','english'}:
        translation_state = 'NOT_REQUIRED_NATIVE_ENGLISH'
    elif translation_exists(root, materialized_source, sha):
        translation_state = 'TRANSLATION_ALREADY_PRESENT'
    else:
        translation_state = 'READY_FOR_TRANSLATION'

    cross = {
        'schema_version': '1.0',
        'file_library_id': ref['file_library_id'],
        'reference_id': ref['reference_id'],
        'reference_path': reference_path.relative_to(root).as_posix(),
        'materialization_status': status,
        'materialization_basis': args.materialization_basis,
        'source_sha256': sha,
        'reported_sha256': reported,
        'reported_hash_verification': 'MATCH' if reported else 'NO_REPORTED_HASH',
        'source_path': source_rel,
        'document_id': document_id,
        'source_language': source_language,
        'translation_state': translation_state,
        'recorded_at': datetime.now(timezone.utc).isoformat(),
    }
    cross_path.write_text(json.dumps(cross, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'outcome': status, 'crosswalk': cross_path.relative_to(root).as_posix(), 'source_sha256': sha, 'translation_state': translation_state}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
