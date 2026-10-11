"""Historical verification must use pinned bytes without restoring payloads."""
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.verify_canonical_snapshot import BASE_PATH, archived_bytes, main, sha_bytes


class CanonicalSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Snapshot test')
        self.git('config', 'user.email', 'snapshot@example.invalid')
        buffer = io.BytesIO()
        content = b'historical source\n'
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('snapshot/source.txt', content)
        self.data = {'snapshot.zip': buffer.getvalue(), 'synthetic.bundle': b'historical bundle'}
        for name, data in self.data.items():
            path = self.root / 'catalog/corpus/source-bundles' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.git('add', 'catalog')
        self.git('commit', '-qm', 'Preserve test snapshot')
        self.commit = self.git('rev-parse', 'HEAD').strip()
        artifacts = []
        for name, data in self.data.items():
            path = 'catalog/corpus/source-bundles/' + name
            artifacts.append({
                'commit': self.commit, 'path': path,
                'legacy_paths': [path, path.removeprefix('catalog/')],
                'git_blob': self.git('rev-parse', f'{self.commit}:{path}').strip(),
                'sha256': sha_bytes(data), 'bytes': len(data),
            })
            (self.root / path).unlink()
        self.index = {'schema': 'tare.tools/operational-archives/1', 'artifacts': artifacts}
        self.write_index()
        base = self.root / BASE_PATH
        base.mkdir(parents=True)
        row = f'{sha_bytes(content)}  source.txt'
        self.baseline = {
            'source': {'preservedPath': 'corpus/source-bundles/snapshot.zip',
                       'archiveSha256': sha_bytes(self.data['snapshot.zip'])},
            'contentIdentity': {'treeSha256': sha_bytes(row.encode())},
            'archiveEvidence': {'fileCount': 1},
            'syntheticGitImport': {'bundlePath': 'corpus/source-bundles/synthetic.bundle',
                                   'bundleSha256': sha_bytes(self.data['synthetic.bundle'])},
        }
        (base / 'BASELINE.json').write_text(json.dumps(self.baseline), encoding='utf-8')
        (base / 'TREE_SHA256SUMS.txt').write_text(row + '\n', encoding='utf-8')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True)

    def write_index(self):
        (self.root / 'catalog/OPERATIONAL_ARCHIVES.json').write_text(
            json.dumps(self.index), encoding='utf-8')

    def test_verifies_removed_payloads_and_does_not_restore_them(self):
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*') if p.is_file())
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(0, main(self.root))
        self.assertIn('PASS canonical snapshot: files=1', output.getvalue())
        after = sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*') if p.is_file())
        self.assertEqual(before, after)

    def test_legacy_alias_is_bound_to_the_original_blob(self):
        path = 'corpus/source-bundles/snapshot.zip'
        self.assertEqual(self.data['snapshot.zip'], archived_bytes(self.root, path))
        self.assertEqual(self.data['snapshot.zip'], archived_bytes(self.root, 'catalog/' + path))

    def test_rejects_tampered_receipts(self):
        for key, value in [('sha256', '0' * 64), ('bytes', 1), ('git_blob', '0' * 40)]:
            with self.subTest(key=key):
                artifact = self.index['artifacts'][0]
                old = artifact[key]
                artifact[key] = value
                self.write_index()
                with self.assertRaisesRegex(ValueError, 'mismatch'):
                    archived_bytes(self.root, artifact['legacy_paths'][0])
                artifact[key] = old

    def test_rejects_mutable_or_absent_commits(self):
        for commit in ['HEAD', '0' * 40]:
            with self.subTest(commit=commit):
                artifact = self.index['artifacts'][0]
                artifact['commit'] = commit
                self.write_index()
                with self.assertRaises(ValueError):
                    archived_bytes(self.root, artifact['legacy_paths'][0])

    def test_rejects_unsafe_paths(self):
        for path in ['../snapshot.zip', '/snapshot.zip', 'C:/snapshot.zip', 'a\\b', 'a//b']:
            with self.subTest(path=path):
                artifact = self.index['artifacts'][0]
                artifact['path'] = path
                self.write_index()
                with self.assertRaisesRegex(ValueError, 'repository-relative'):
                    archived_bytes(self.root, artifact['legacy_paths'][0])

    def test_per_file_identity_is_still_checked(self):
        (self.root / BASE_PATH / 'TREE_SHA256SUMS.txt').write_text('tampered\n', encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(1, main(self.root))
        self.assertIn('per-file sums mismatch', output.getvalue())


if __name__ == '__main__':
    unittest.main()
