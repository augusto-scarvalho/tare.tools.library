# GitHub Backend — TARGET

Preferred progression:

1. local filesystem + manual Git commit;
2. local Git backend creating a branch and commit;
3. GitHub CLI adapter for controlled operator-driven publishing;
4. GitHub App with repository-scoped permissions and PR-first writes;
5. optional ChatGPT/Codex bridge calling only narrow publication operations.

Recommended external operations:

- `publish_research(packet)`
- `publish_experiment(packet)`
- `publish_archaeology(packet)`
- `propose_canonical_promotion(packet)` — PR/proposal only; no self-ratification.

Avoid exposing generic `write_file(repo,path,bytes)` to the chat surface.
