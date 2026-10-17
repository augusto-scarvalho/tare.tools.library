#!/usr/bin/env python3
"""Materialize exact bytes for a File Library discovery reference.

This command never reconstructs content from snippets. It requires a caller-supplied
exact-byte file and records how that file was acquired. Reference sidecars remain
immutable discovery evidence; materialization is represented by a separate crosswalk.

Run with one writer per root. Publication is atomic per file, not across source,
manifest and crosswalk. Replay reconciles complete source/manifest artifacts;
an abrupt exit may leave an unpublished temporary file. Concurrent path changes
and power-loss durability are outside this command's guarantees.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import os
import shutil
import sys
import tempfile

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


def component(value: str) -> str:
    if (not isinstance(value, str) or not value or value in {'.', '..'}
            or value != value.strip() or value.endswith('.')
            or re.search(r'[<>:"/\\|?*\x00-\x1f]', value)
            or value.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL',
                *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}):
        raise ValueError('invalid identity/path component')
    return value


def contained(root: Path, path: Path, *, directory=False) -> Path:
    path.relative_to(root)
    for part in [path, *path.parents]:
        if part == root:
            break
        if part.is_symlink() or part.is_junction():
            raise ValueError(f'linked path: {part}')
        if part.exists() and (part != path or directory) and not part.is_dir():
            raise ValueError(f'not a directory: {part}')
    path.resolve().relative_to(root)
    if not directory and path.exists() and not path.is_file():
        raise ValueError(f'not a file: {path}')
    return path


def record_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('invalid recorded path')
    for part in value.split('/'):
        component(part)
    return contained(root, root / value)


def atomic_json(path: Path, record: dict) -> None:
    # Atomic per record only: source, manifest and crosswalk are NOT a transaction.
    data = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    temporary = None
    try:
        with tempfile.NamedTemporaryFile('w', dir=path.parent, encoding='utf-8',
                                         delete=False, suffix='.tmp') as f:
            temporary = Path(f.name)
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def find_existing_by_hash(root: Path, sha: str) -> tuple[dict, Path] | None:
    found = None
    for p in sorted((root / 'catalog/corpus' / 'manifests').glob('*.json')):
        try:
            m = load(p)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(m, dict):
            continue
        provenance = m.get('provenance', {})
        if not isinstance(provenance, dict) or provenance.get('source_sha256') != sha:
            continue
        contained(root, p)
        if 'source_path' not in provenance:
            raise ValueError('existing source path missing')
        source = record_path(root, provenance['source_path'])
        component(m['document_id'])
        for key in ('file_library_id', 'reference_id'):
            if key in provenance:
                component(provenance[key])
        if provenance.get('source_sha256') == sha:
            if not source.is_file() or digest(source) != sha:
                raise ValueError('existing source hash mismatch/missing')
            found = found or (m, source)
    return found


def translation_exists(root: Path, source_path: Path, source_sha: str) -> bool:
    found = False
    for p in sorted((root / 'catalog/corpus' / 'manifests' / 'translations' / 'en').glob('*.json')):
        try:
            m = load(p)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(m, dict) or m.get('source_sha256') != source_sha:
            continue
        contained(root, p)
        recorded = record_path(root, m['source_path'])
        if m.get('source_sha256') == source_sha and recorded == source_path:
            found = True
    return found


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
    reference_path = Path(os.path.abspath(args.reference))
    contained(root, reference_path)
    component(args.document_id)
    component(args.batch)
    for directory in ('catalog/identity-crosswalk', 'catalog/corpus/original',
                      'catalog/corpus/manifests', 'catalog/corpus/manifests/translations/en'):
        contained(root, root / directory, directory=True)
    source = Path(args.source).resolve()
    if not reference_path.is_file() or not source.is_file():
        print('DENY reference/source missing')
        return 2
    ref = load(reference_path)
    component(ref['file_library_id'])
    component(ref['reference_id'])
    if not isinstance(ref['title'], str) or not ref['title'].strip():
        raise ValueError('invalid reference title')
    if ref.get('availability') != 'LIBRARY_REFERENCE_ONLY' or ref.get('materialized_bytes') is not False:
        print('DENY reference is not immutable reference-only record')
        return 2
    sha = digest(source)
    reported = ref.get('reported_sha256')
    if reported and reported != sha:
        print('DENY REPORTED_SHA256_MISMATCH', reported, sha)
        return 3

    cross_dir = root / 'catalog' / 'identity-crosswalk'
    cross_path = contained(root, cross_dir / f"{ref['file_library_id']}.json")

    source_language = args.source_language or ref.get('native_language') or 'unknown'
    contexts = args.context or ref.get('suggested_contexts') or []
    if not isinstance(source_language, str) or not source_language.strip():
        raise ValueError('invalid source language')
    if not isinstance(contexts, list) or not all(isinstance(c, str) and c.strip() for c in contexts):
        raise ValueError('invalid contexts')
    if not contexts:
        print('DENY at least one context required')
        return 2

    original_filename = safe_name(ref.get('title') or source.name)
    if not Path(original_filename).suffix and source.suffix:
        original_filename += source.suffix
    component(original_filename)
    unique_name = component(f"{ref['file_library_id']}__{original_filename}")
    target_dir = contained(root, root / 'catalog/corpus/original' / args.batch, directory=True)
    target = contained(root, target_dir / unique_name)
    manifest_path = contained(root, root / 'catalog/corpus/manifests' / f'{unique_name}.json')
    if reference_path in {target, manifest_path, cross_path} or source in {manifest_path, cross_path}:
        raise ValueError('input/output alias')
    existing = find_existing_by_hash(root, sha)
    # A named manifest must never be overwritten, even if another hash match exists.
    if manifest_path.exists():
        named = load(manifest_path)
        if (named.get('provenance', {}).get('source_sha256') != sha
                or named.get('provenance', {}).get('file_library_id') != ref['file_library_id']
                or named.get('provenance', {}).get('reference_id') != ref['reference_id']
                or named.get('provenance', {}).get('source_path') != target.relative_to(root).as_posix()
                or named.get('document_id') != args.document_id):
            raise ValueError('manifest collision')
    if target.exists() and digest(target) != sha:
        raise ValueError('target collision/hash mismatch')
    if existing:
        manifest, materialized_source = existing
        document_id = manifest['document_id']
        status = 'ALREADY_MATERIALIZED_BY_HASH'
        source_rel = materialized_source.relative_to(root).as_posix()
    else:
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
                'size_bytes': source.stat().st_size,
                'original_filename': ref['title'],
                'file_library_id': ref['file_library_id'],
                'reference_id': ref['reference_id'],
                'materialization_basis': args.materialization_basis,
                'notes': 'Exact-byte materialization of a prior File Library discovery reference; discovery reference is preserved separately.'
            }
        }
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
    if cross_path.exists():
        old = load(cross_path)
        recorded_source = record_path(root, old['source_path'])
        record_path(root, old['reference_path'])
        component(old['document_id'])
        if (not existing or not recorded_source.is_file() or digest(recorded_source) != sha
                or any(old.get(k) != cross[k] for k in
                       ('file_library_id', 'reference_id', 'reference_path',
                        'source_sha256', 'source_path', 'document_id'))):
            raise ValueError('crosswalk collision or invalid backing source')
        print('PASS ALREADY_CROSSWALKED', cross_path)
        return 0

    # All semantic/path checks precede mkdir/copy. Single-writer operation; no
    # multi-file atomicity or protection against concurrent path substitution.
    if not existing:
        target_dir.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            # Publish only verified, complete bytes. The second collision check
            # preserves an existing target within the single-writer contract.
            temporary = None
            try:
                with tempfile.NamedTemporaryFile('wb', dir=target_dir,
                                                 delete=False, suffix='.tmp') as dst:
                    temporary = Path(dst.name)
                    with source.open('rb') as src:
                        shutil.copyfileobj(src, dst)
                    dst.flush()
                    os.fsync(dst.fileno())
                if digest(temporary) != sha:
                    raise ValueError('copy hash mismatch')
                if target.exists():
                    raise ValueError('target collision during copy')
                os.replace(temporary, target)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        if digest(target) != sha:
            raise ValueError('copy hash mismatch; retained for reconciliation')
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_json(manifest_path, manifest)
    cross_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(cross_path, cross)
    print(json.dumps({'outcome': status, 'crosswalk': cross_path.relative_to(root).as_posix(), 'source_sha256': sha, 'translation_state': translation_state}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        print(f'DENY {exc}')
        raise SystemExit(2)
