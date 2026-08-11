# GitHub CLI Backend — controlled edge adapter

Status in this bootstrap: **CURRENT for planning/dry-run and fail-closed authorization gates; environment qualification for real remote effects is NOT COMPLETE**.

Flow:

`Publication Packet → canonical policy → local Git plan → GitHub plan → explicit remote-effect gate → origin verification → gh auth → push branch → PR`

Defaults:
- dry-run;
- no local branch creation during GitHub dry-run;
- no remote effects unless both `--apply` and `--allow-remote-effects` are present;
- repository slug must be explicit (`OWNER/NAME`);
- configured `origin` must resolve to the same GitHub repository before push;
- publication opens a PR and does not merge or ratify architecture;
- `gh` authentication/runtime availability is qualification, not assumed capability.

Dry-run:

```bash
python -m tare_tools_publisher.cli incoming/foo/PUBLISH_MANIFEST.json \
  --backend github-cli \
  --repo-root /path/to/tare.tools.research \
  --github-repo OWNER/tare.tools.research
```

Remote application is intentionally a two-key operation:

```bash
... --apply --allow-remote-effects
```

No remote effect was executed while building this bootstrap.
