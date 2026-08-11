# Local Git Backend — v0.1

Status: **CURRENT in the document-repository bootstrap**. This backend performs local Git effects only. It never contacts a remote.

## Boundary

`Publication Packet → policy/route → pinned base SHA → disposable worktree → local branch + commit → receipt`

The user's main worktree and index are not used for publication writes or staging. The backend pins `base_ref` once, creates a detached disposable worktree at that SHA, creates a deterministic local branch derived from `document_id + manifest hash`, copies only declared artifacts plus `PUBLISH_MANIFEST.json`, commits, removes the disposable worktree, and returns a receipt.

## Defaults

- dry-run unless `--apply`;
- no remote commands;
- no push/PR;
- branch collision is fail-closed;
- routing/promotion policy remains the same as the filesystem backend;
- canonical `tare-tools` publication still requires `canonical_change=true` plus a `promotion_packet`.

## CLI

```bash
python -m tare_tools_publisher.cli incoming/foo/PUBLISH_MANIFEST.json \
  --backend git-local \
  --repo-root /path/to/tare.tools.research
```

Apply locally:

```bash
python -m tare_tools_publisher.cli incoming/foo/PUBLISH_MANIFEST.json \
  --backend git-local \
  --repo-root /path/to/tare.tools.research \
  --apply
```

An applied run creates a **local branch and commit only**. GitHub remains a separate future backend/effect boundary.

## Local publication record and replay

Every committed publication contains `PUBLICATION_RECORD.json` with the pinned base SHA, deterministic branch, manifest digest, destination and artifact digests. Replaying the exact same packet returns `ALREADY_PUBLISHED` and the existing local commit without creating another commit. A branch with the same deterministic identity but missing/mismatching the record is a fail-closed collision.
