#!/usr/bin/env python3
"""Verify preserved historical bytes in Git without materializing the harness."""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = Path('docs/references/baselines/private-github-main-2026-08-05')


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archived_bytes(root: Path, legacy_path: str) -> bytes:
    """Resolve a historical path to one pinned, locally available Git blob."""
    index = json.loads((root / 'catalog/OPERATIONAL_ARCHIVES.json').read_text(encoding='utf-8'))
    if index.get('schema') != 'tare.tools/operational-archives/1':
        raise ValueError('unsupported operational archive schema')
    matches = [a for a in index['artifacts'] if legacy_path in a['legacy_paths']]
    if len(matches) != 1:
        raise ValueError(f'expected one archived artifact for {legacy_path}')
    artifact = matches[0]
    commit, path = artifact['commit'], artifact['path']
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('archive commit must be a full immutable Git SHA')
    if (not path or PurePosixPath(path).is_absolute() or '\\' in path or ':' in path
            or any(part in ('', '.', '..') for part in path.split('/'))):
        raise ValueError('archive path must be a repository-relative Git path')
    # Do not let partial-clone lazy fetching turn verification into a network operation.
    result = subprocess.run(
        ['git', '-C', str(root), 'cat-file', 'blob', f'{commit}:{path}'],
        env={**os.environ, 'GIT_NO_LAZY_FETCH': '1'}, capture_output=True, check=False,
    )
    if result.returncode:
        raise ValueError(f'archived object is unavailable locally: {commit}:{path}')
    data = result.stdout
    if len(data) != artifact['bytes'] or sha_bytes(data) != artifact['sha256']:
        raise ValueError(f'archived artifact size or SHA-256 mismatch: {path}')
    blob = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
    if blob != artifact['git_blob']:
        raise ValueError(f'archived Git blob identity mismatch: {path}')
    return data


def main(root: Path = ROOT) -> int:
    base = root / BASE_PATH
    d = json.loads((base / 'BASELINE.json').read_text(encoding='utf-8'))
    try:
        archive = archived_bytes(root, d['source']['preservedPath'])
        bundle = archived_bytes(root, d['syntheticGitImport']['bundlePath'])
    except (ValueError, KeyError, OSError) as exc:
        print('FAIL', exc)
        return 1
    fails = []
    if sha_bytes(archive) != d['source']['archiveSha256']:
        fails.append('archive sha mismatch')
    # Inspect entries in memory only; never extract, execute or import their contents.
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        infos = [i for i in z.infolist() if not i.is_dir()]
        prefix = infos[0].filename.split('/')[0] + '/' if infos else ''
        pairs = []
        for info in infos:
            rel = info.filename[len(prefix):] if info.filename.startswith(prefix) else info.filename
            pairs.append((rel, f'{sha_bytes(z.read(info))}  {rel}'))
        rows = [row for _, row in sorted(pairs, key=lambda pair: pair[0])]
        tree = sha_bytes(('\n'.join(rows)).encode())
    if tree != d['contentIdentity']['treeSha256']:
        fails.append('content tree sha mismatch')
    if len(rows) != d['archiveEvidence']['fileCount']:
        fails.append('file count mismatch')
    expected = (base / 'TREE_SHA256SUMS.txt').read_text(encoding='utf-8').splitlines()
    if sorted(rows) != sorted(expected):
        fails.append('per-file sums mismatch')
    if sha_bytes(bundle) != d['syntheticGitImport']['bundleSha256']:
        fails.append('synthetic git bundle sha mismatch')
    if fails:
        for failure in fails:
            print('FAIL', failure)
        return 1
    print(f"PASS canonical snapshot: files={len(rows)} archive={d['source']['archiveSha256'][:12]} "
          f"tree={tree[:12]} bundle={d['syntheticGitImport']['bundleSha256'][:12]}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
