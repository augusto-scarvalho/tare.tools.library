# Changelog

Notable changes to `tare.tools.library` are recorded here, newest first.

## Unreleased

- The pre-push hook now checks unpublished commits' author and committer emails via `tools/push_preflight.py`, refusing any non-GitHub-noreply address before pushing branches or tags (and cleanly ignoring an empty line forwarded by a hook wrapper).
- First public release. The repository starts from a single commit; earlier history is not published. It contains the
  Library-owned research in `docs/research/` and the derived, rebuildable retrieval index (lexical search and an
  incremental SQLite vector index) with its tools and tests.
