from __future__ import annotations

from dataclasses import dataclass, asdict
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from .policy import route, validate
from .translation import file_hash, validate_pages_translation


class GitBackendError(RuntimeError):
    pass


@dataclass(frozen=True)
class GitPublicationReceipt:
    backend: str
    applied: bool
    changed: bool
    outcome: str
    document_id: str
    destination: str
    base_sha: str
    branch: str
    commit_sha: str | None
    manifest_sha256: str
    remote_effects: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


def _run(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise GitBackendError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc


def _file_hash(path: Path) -> str:
    return file_hash(path)


def _manifest_hash(packet: Path) -> str:
    return _file_hash(packet)


def _blob(repo: Path, revision: str, path: str) -> bytes:
    shown = subprocess.run(["git", "-C", str(repo), "show", f"{revision}:{path}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if shown.returncode:
        raise GitBackendError(f"packet path is not present in pinned base: {path}")
    return shown.stdout


@contextmanager
def _pinned_packet(repo: Path, packet: Path, base_sha: str):
    """Materialize packet bytes from Git, not checkout conversion filters."""
    try:
        rel = packet.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        yield packet
        return
    manifest_bytes = _blob(repo, base_sha, rel)
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GitBackendError(f"pinned manifest is invalid: {exc}") from exc
    with tempfile.TemporaryDirectory(prefix="tare-tools-publisher-packet-") as td:
        restored = Path(td) / "PUBLISH_MANIFEST.json"
        restored.write_bytes(manifest_bytes)
        for artifact in manifest.get("artifacts", []):
            artifact_path = Path(artifact)
            if artifact_path.is_absolute() or ".." in artifact_path.parts:
                raise GitBackendError(f"unsafe artifact path: {artifact}")
            destination = restored.parent / artifact_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(_blob(repo, base_sha, f"{Path(rel).parent.as_posix()}/{artifact}"))
        decision_rel = f"{Path(rel).parent.as_posix()}/EDITORIAL_DECISION.json"
        decision = subprocess.run(["git", "-C", str(repo), "show", f"{base_sha}:{decision_rel}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if decision.returncode == 0:
            (restored.parent / "EDITORIAL_DECISION.json").write_bytes(decision.stdout)
        yield restored


def _safe_branch_component(value: str) -> str:
    out = []
    for c in value.lower():
        out.append(c if c.isalnum() or c in {"-", "_"} else "-")
    s = "".join(out).strip("-")
    while "--" in s:
        s = s.replace("--", "-")
    return s or "document"


def planned_branch(document_id: str, manifest_sha256: str, editorial_decision_sha256: str | None = None) -> str:
    identity = manifest_sha256
    if editorial_decision_sha256:
        identity = sha256(f"{manifest_sha256}:{editorial_decision_sha256}".encode()).hexdigest()
    return f"docs/publish/{_safe_branch_component(document_id)}-{identity[:12]}"


def _load_and_validate_packet(packet: Path) -> tuple[dict, str]:
    manifest = json.loads(packet.read_text(encoding="utf-8"))
    errors = validate(manifest)
    if errors:
        raise GitBackendError("policy denied: " + "; ".join(errors))
    destination = route(manifest)
    return manifest, destination


def _packet_hash(packet: Path, manifest: dict) -> str:
    rows = [{"path": "PUBLISH_MANIFEST.json", "sha256": _file_hash(packet)}]
    rows.extend({"path": rel, "sha256": _file_hash(packet.parent / rel)} for rel in manifest["artifacts"])
    return sha256(json.dumps(sorted(rows, key=lambda row: row["path"]), separators=(",", ":")).encode()).hexdigest()


def _validate_editorial_decision(packet: Path, manifest: dict, manifest_sha256: str) -> tuple[dict | None, str | None]:
    path = packet.parent / "EDITORIAL_DECISION.json"
    pages_requested = "pages" in manifest.get("requested_channels", [])
    if not path.is_file():
        if pages_requested:
            raise GitBackendError("EDITORIAL_DECISION.json required before publishing a packet that requests Pages")
        return None, None
    try:
        decision = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GitBackendError(f"invalid editorial decision JSON: {exc}") from exc
    errors=[]
    version = decision.get("decision_version")
    if version not in {"1.0", "1.1"}: errors.append("decision_version must be 1.0 or 1.1")
    if not isinstance(decision.get("decision_id"), str) or not decision["decision_id"].strip(): errors.append("decision_id required")
    if decision.get("document_id") != manifest.get("document_id"): errors.append("editorial decision document_id mismatch")
    if decision.get("manifest_sha256") != manifest_sha256: errors.append("editorial decision manifest_sha256 mismatch")
    if decision.get("decision") not in {"accept","revise","reject","park"}: errors.append("invalid editorial decision")
    if not isinstance(decision.get("pages_approved"), bool): errors.append("editorial pages_approved must be boolean")
    reviewer=decision.get("reviewer")
    if not isinstance(reviewer, dict) or not reviewer.get("name") or reviewer.get("role") != "editorial-reviewer":
        errors.append("editorial reviewer identity/role required")
    if not isinstance(decision.get("reviewed_at"), str) or not decision["reviewed_at"].strip(): errors.append("reviewed_at required")
    if version == "1.1":
        if decision.get("packet_sha256") != _packet_hash(packet, manifest): errors.append("editorial decision packet_sha256 mismatch")
        submission = decision.get("submission")
        if not isinstance(submission, dict) or not all(isinstance(submission.get(k), str) and submission[k].strip() for k in ("repository", "head_sha", "author_login")) or not isinstance(submission.get("pr_number"), int):
            errors.append("editorial submission identity required")
        identity = reviewer.get("identity_ref") if isinstance(reviewer, dict) else None
        author = submission.get("author_login") if isinstance(submission, dict) else None
        if isinstance(identity, str) and identity.removeprefix("github:") == author:
            errors.append("submitter cannot approve their own editorial decision")
    if decision.get("pages_approved") and decision.get("decision") != "accept": errors.append("Pages approval requires decision=accept")
    if decision.get("pages_approved") and not pages_requested: errors.append("Pages approval cannot be granted when Pages was not requested")
    if errors:
        raise GitBackendError("editorial decision denied: " + "; ".join(errors))
    translation_errors, _ = validate_pages_translation(packet.parent, manifest, legacy_decision=version == "1.0")
    if translation_errors:
        raise GitBackendError("translation denied: " + "; ".join(translation_errors))
    return decision, _file_hash(path)


def _validate_artifacts(packet: Path, manifest: dict) -> list[tuple[Path, str]]:
    parent = packet.parent.resolve()
    artifacts: list[tuple[Path, str]] = []
    for rel in manifest["artifacts"]:
        src = (parent / rel).resolve()
        if parent != src.parent and parent not in src.parents:
            raise GitBackendError(f"artifact escapes packet: {rel}")
        if not src.is_file():
            raise GitBackendError(f"missing artifact: {rel}")
        artifacts.append((src, src.name))
    return artifacts


def _artifact_digests(artifacts: list[tuple[Path, str]]) -> dict[str, str]:
    return {name: _file_hash(src) for src, name in artifacts}


def _publication_record(
    manifest: dict,
    destination: str,
    receipt: GitPublicationReceipt,
    artifacts: list[tuple[Path, str]],
    decision: dict | None,
    decision_sha256: str | None,
) -> dict:
    editorial = None
    if decision is not None:
        editorial = {
            "decision_id": decision["decision_id"],
            "decision": decision["decision"],
            "pages_approved": decision["pages_approved"],
            "reviewer": decision["reviewer"],
            "reviewed_at": decision["reviewed_at"],
            "sha256": decision_sha256,
        }
    translation_errors, projection = validate_pages_translation(
        artifacts[0][0].parent, manifest, legacy_decision=bool(decision and decision.get("decision_version") == "1.0")
    )
    if translation_errors:
        raise GitBackendError("translation denied: " + "; ".join(translation_errors))
    return {
        "record_version": "1.2",
        "backend": "git-local",
        "document_id": manifest["document_id"],
        "destination": destination,
        "base_sha": receipt.base_sha,
        "branch": receipt.branch,
        "manifest_sha256": receipt.manifest_sha256,
        "artifact_sha256": _artifact_digests(artifacts),
        "primary_artifact": manifest.get("primary_artifact"),
        "requested_channels": manifest.get("requested_channels", []),
        "pages_approved": bool(decision and decision.get("pages_approved") is True),
        "editorial_decision": editorial,
        "pages_projection": projection or {
            "language": "en",
            "primary_artifact": manifest.get("primary_artifact"),
            "metadata_artifact": "document-metadata.json",
        },
        "remote_effects": False,
    }


def _existing_publication(
    repo_root: Path,
    branch: str,
    destination: str,
    manifest_sha256: str,
    editorial_decision_sha256: str | None,
) -> str | None:
    ref = f"refs/heads/{branch}"
    if _run(repo_root, "show-ref", "--verify", ref, check=False).returncode != 0:
        return None
    commit_sha = _run(repo_root, "rev-parse", branch).stdout.strip()
    record_path = f"{destination}/PUBLICATION_RECORD.json"
    shown = _run(repo_root, "show", f"{branch}:{record_path}", check=False)
    if shown.returncode != 0:
        raise GitBackendError(f"branch collision without publication record: {branch}")
    try:
        record = json.loads(shown.stdout)
    except json.JSONDecodeError as exc:
        raise GitBackendError(f"branch collision with invalid publication record: {branch}") from exc
    observed_decision_sha = (record.get("editorial_decision") or {}).get("sha256")
    if (
        record.get("manifest_sha256") != manifest_sha256
        or observed_decision_sha != editorial_decision_sha256
        or record.get("branch") != branch
        or record.get("destination") != destination
    ):
        raise GitBackendError(f"branch collision with mismatched publication identity: {branch}")
    return commit_sha


def plan(packet: Path, repo_root: Path, *, base_ref: str = "HEAD") -> GitPublicationReceipt:
    packet = packet.resolve()
    repo_root = repo_root.resolve()
    if not packet.is_file():
        raise GitBackendError(f"packet not found: {packet}")
    if _run(repo_root, "rev-parse", "--is-inside-work-tree", check=False).stdout.strip() != "true":
        raise GitBackendError(f"not a git worktree: {repo_root}")
    base_sha = _run(repo_root, "rev-parse", "--verify", base_ref).stdout.strip()
    with _pinned_packet(repo_root, packet, base_sha) as pinned:
        manifest, destination = _load_and_validate_packet(pinned)
        _validate_artifacts(pinned, manifest)
        mh = _manifest_hash(pinned)
        _, decision_sha = _validate_editorial_decision(pinned, manifest, mh)
        branch = planned_branch(manifest["document_id"], mh, decision_sha)
        existing_commit = _existing_publication(repo_root, branch, destination, mh, decision_sha)
    return GitPublicationReceipt(
        backend="git-local",
        applied=False,
        changed=False,
        outcome="ALREADY_PUBLISHED" if existing_commit else "PLANNED",
        document_id=manifest["document_id"],
        destination=destination,
        base_sha=base_sha,
        branch=branch,
        commit_sha=existing_commit,
        manifest_sha256=mh,
    )


def publish(
    packet: Path,
    repo_root: Path,
    *,
    apply: bool = False,
    base_ref: str = "HEAD",
) -> GitPublicationReceipt:
    receipt = plan(packet, repo_root, base_ref=base_ref)
    if not apply:
        return receipt
    if receipt.outcome == "ALREADY_PUBLISHED":
        return GitPublicationReceipt(
            backend=receipt.backend, applied=True, changed=False, outcome="ALREADY_PUBLISHED",
            document_id=receipt.document_id, destination=receipt.destination, base_sha=receipt.base_sha,
            branch=receipt.branch, commit_sha=receipt.commit_sha, manifest_sha256=receipt.manifest_sha256,
        )

    packet = packet.resolve()
    repo_root = repo_root.resolve()
    with _pinned_packet(repo_root, packet, receipt.base_sha) as pinned:
        manifest, destination = _load_and_validate_packet(pinned)
        artifacts = _validate_artifacts(pinned, manifest)
        decision, decision_sha = _validate_editorial_decision(pinned, manifest, receipt.manifest_sha256)
        # Main worktree/index are never used for file writes or staging. The base SHA
        # is pinned once by plan(); publication happens in a disposable detached worktree.
        with tempfile.TemporaryDirectory(prefix="tare-tools-publisher-") as td:
            wt = Path(td) / "worktree"
            _run(repo_root, "worktree", "add", "--detach", str(wt), receipt.base_sha)
            try:
                _run(wt, "switch", "-c", receipt.branch)
                target = (wt / destination).resolve()
                if wt != target and wt not in target.parents:
                    raise GitBackendError("target escapes repository")
                target.mkdir(parents=True, exist_ok=False)
                for src, name in artifacts:
                    shutil.copy2(src, target / name)
                shutil.copy2(pinned, target / "PUBLISH_MANIFEST.json")
                if decision is not None:
                    shutil.copy2(pinned.parent / "EDITORIAL_DECISION.json", target / "EDITORIAL_DECISION.json")
                record = _publication_record(manifest, destination, receipt, artifacts, decision, decision_sha)
                (target / "PUBLICATION_RECORD.json").write_text(
                    json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )

                rel_target = target.relative_to(wt).as_posix()
                _run(wt, "add", "--", rel_target)
                staged = _run(wt, "diff", "--cached", "--name-only", "--", rel_target).stdout.splitlines()
                if not staged:
                    raise GitBackendError("nothing staged for publication")
                _run(
                    wt,
                    "-c", "user.name=tare-tools-publisher",
                    "-c", "user.email=publisher@tare.tools",
                    "commit", "-m", f"docs: publish {manifest['document_id']}",
                )
                commit_sha = _run(wt, "rev-parse", "HEAD").stdout.strip()
            finally:
                _run(repo_root, "worktree", "remove", "--force", str(wt), check=False)
                _run(repo_root, "worktree", "prune", check=False)

    return GitPublicationReceipt(
        backend=receipt.backend,
        applied=True,
        changed=True,
        outcome="PUBLISHED",
        document_id=receipt.document_id,
        destination=receipt.destination,
        base_sha=receipt.base_sha,
        branch=receipt.branch,
        commit_sha=commit_sha,
        manifest_sha256=receipt.manifest_sha256,
    )
