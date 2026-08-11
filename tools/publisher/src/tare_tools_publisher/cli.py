from pathlib import Path
import argparse
import json
import shutil

from .policy import validate, route
from .git_backend import GitBackendError, publish as git_publish
from .github_cli_backend import GitHubCliBackendError, publish as github_publish


def _filesystem_publish(packet: Path, repo_root: Path | None, apply: bool) -> int:
    manifest = json.loads(packet.read_text(encoding="utf-8"))
    errors = validate(manifest)
    if errors:
        for error in errors:
            print("DENY", error)
        return 2
    destination = route(manifest)
    print("ALLOW route=", destination)
    if not apply:
        print("DRY_RUN no files written")
        return 0
    if repo_root is None:
        print("DENY --repo-root required with --apply")
        return 2
    root = repo_root.resolve()
    target = (root / destination).resolve()
    if root != target and root not in target.parents:
        print("DENY target escapes repo")
        return 2
    target.mkdir(parents=True, exist_ok=True)
    for rel in manifest["artifacts"]:
        src = (packet.parent / rel).resolve()
        if packet.parent != src.parent and packet.parent not in src.parents:
            print("DENY artifact escapes packet")
            return 2
        if not src.is_file():
            print("DENY missing artifact", rel)
            return 2
        out = target / src.name
        if out.exists():
            print("DENY collision", out)
            return 2
        shutil.copy2(src, out)
        print("WROTE", out)
    shutil.copy2(packet, target / "PUBLISH_MANIFEST.json")
    print("DONE")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("packet")
    ap.add_argument("--backend", choices=["filesystem", "git-local", "github-cli"], default="filesystem")
    ap.add_argument("--repo-root")
    ap.add_argument("--base-ref", default="HEAD")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--github-repo", help="OWNER/NAME; required for github-cli")
    ap.add_argument("--allow-remote-effects", action="store_true", help="second explicit gate for GitHub push/PR effects")
    args = ap.parse_args()

    packet = Path(args.packet).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None

    if args.backend == "filesystem":
        return _filesystem_publish(packet, repo_root, args.apply)

    if repo_root is None:
        print("DENY --repo-root required for git backends")
        return 2
    if args.backend == "git-local":
        try:
            receipt = git_publish(packet, repo_root, apply=args.apply, base_ref=args.base_ref)
        except (GitBackendError, OSError, ValueError, json.JSONDecodeError) as exc:
            print("DENY", exc)
            return 2
        print(json.dumps(receipt.as_dict(), ensure_ascii=False, indent=2))
        if not args.apply:
            print("DRY_RUN no git refs or files written")
        return 0

    if not args.github_repo:
        print("DENY --github-repo OWNER/NAME required for github-cli")
        return 2
    try:
        receipt = github_publish(packet, repo_root, args.github_repo, apply=args.apply, allow_remote_effects=args.allow_remote_effects, base_ref=args.base_ref)
    except (GitHubCliBackendError, GitBackendError, OSError, ValueError, json.JSONDecodeError) as exc:
        print("DENY", exc)
        return 2
    print(json.dumps(receipt.as_dict(), ensure_ascii=False, indent=2))
    if not args.apply:
        print("DRY_RUN no local git refs, remote refs or PRs written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
