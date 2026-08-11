# tare-tools-publisher

Deterministic document-ingestion/publishing boundary for tare.tools.

## CURRENT in this bootstrap

- local filesystem backend;
- local Git backend using disposable worktrees, local branches and commits;
- GitHub CLI backend planning with explicit two-key remote-effect gate (`--apply` + `--allow-remote-effects`);
- manifest validation;
- deterministic destination routing;
- copy-only publication with collision protection;
- dry-run by default;
- unit tests.

## TARGET

Qualify real GitHub remote effects, then prefer a repository-scoped GitHub App or controlled Codex workflow behind the same narrow interface. External write capability must not change routing/authority semantics. See [`docs/GITHUB_CLI_BACKEND.md`](docs/GITHUB_CLI_BACKEND.md).

## Non-goals

- deciding architecture;
- promoting RESEARCH to TARGET;
- arbitrary GitHub filesystem access;
- rewriting historical originals;
- acting as a general-purpose autonomous agent.

## Local Git backend

See [`docs/LOCAL_GIT_BACKEND.md`](docs/LOCAL_GIT_BACKEND.md). It never contacts remotes and is dry-run by default.
