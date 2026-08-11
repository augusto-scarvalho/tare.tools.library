from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path
import json, shutil, subprocess
from .git_backend import GitBackendError, publish as git_publish

class GitHubCliBackendError(RuntimeError):
    pass

@dataclass(frozen=True)
class GitHubPublicationReceipt:
    backend: str
    applied: bool
    remote_effects: bool
    outcome: str
    repository: str
    document_id: str
    branch: str
    base_sha: str
    local_commit_sha: str | None
    planned_commands: tuple[str, ...]
    pr_url: str | None = None
    def as_dict(self): return asdict(self)

def _run(cmd:list[str], cwd:Path|None=None, check:bool=True):
    p=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if check and p.returncode:
        raise GitHubCliBackendError(f"command failed ({p.returncode}): {' '.join(cmd)}: {p.stderr.strip()}")
    return p

def _require_slug(slug:str):
    parts=slug.split('/')
    if len(parts)!=2 or any(not x or x in {'.','..'} for x in parts):
        raise GitHubCliBackendError('repository must be OWNER/NAME')

def _origin_slug(repo_root:Path)->str|None:
    p=_run(['git','-C',str(repo_root),'remote','get-url','origin'],check=False)
    if p.returncode: return None
    u=p.stdout.strip().removesuffix('.git')
    if u.startswith('git@github.com:'): return u.split(':',1)[1]
    marker='github.com/'
    if marker in u: return u.split(marker,1)[1]
    return None

def plan(packet:Path, repo_root:Path, repository:str, *, base_ref:str='HEAD')->GitHubPublicationReceipt:
    _require_slug(repository)
    local=git_publish(packet,repo_root,apply=False,base_ref=base_ref)
    cmds=(
        f"git push --set-upstream origin {local.branch}",
        f"gh pr create --repo {repository} --head {local.branch} --base <DEFAULT_BRANCH> --title 'docs: publish {local.document_id}' --body-file <GENERATED_BODY>",
    )
    return GitHubPublicationReceipt('github-cli',False,False,'PLANNED_REMOTE',repository,local.document_id,local.branch,local.base_sha,local.commit_sha,cmds,None)

def publish(packet:Path, repo_root:Path, repository:str, *, apply:bool=False, allow_remote_effects:bool=False, base_ref:str='HEAD')->GitHubPublicationReceipt:
    planned=plan(packet,repo_root,repository,base_ref=base_ref)
    if not apply: return planned
    if not allow_remote_effects:
        raise GitHubCliBackendError('REMOTE_EFFECTS_NOT_AUTHORIZED: pass --allow-remote-effects explicitly')
    gh=shutil.which('gh')
    if not gh:
        raise GitHubCliBackendError('GH_CLI_UNAVAILABLE')
    local=git_publish(packet,repo_root,apply=True,base_ref=base_ref)
    origin=_origin_slug(repo_root)
    if origin != repository:
        raise GitHubCliBackendError(f'ORIGIN_REPOSITORY_MISMATCH expected={repository} observed={origin!r}')
    auth=_run([gh,'auth','status','--hostname','github.com'],check=False)
    if auth.returncode:
        raise GitHubCliBackendError('GH_AUTH_NOT_READY')
    # Determine default branch without mutating remote.
    view=_run([gh,'repo','view',repository,'--json','defaultBranchRef','--jq','.defaultBranchRef.name'])
    default_branch=view.stdout.strip()
    if not default_branch: raise GitHubCliBackendError('DEFAULT_BRANCH_UNKNOWN')
    _run(['git','-C',str(repo_root),'push','--set-upstream','origin',local.branch])
    body=(f"Automated document publication proposal.\n\nDocument: `{local.document_id}`\nBase: `{local.base_sha}`\nLocal commit: `{local.commit_sha}`\n\nPublication is content ingestion only; it does not ratify architecture.\n")
    # gh can read body from stdin; avoid temp files and shell interpolation.
    pr=subprocess.run([gh,'pr','create','--repo',repository,'--head',local.branch,'--base',default_branch,'--title',f'docs: publish {local.document_id}','--body',body],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if pr.returncode:
        raise GitHubCliBackendError(f'PR_CREATE_FAILED: {pr.stderr.strip()}')
    return GitHubPublicationReceipt('github-cli',True,True,'PR_CREATED',repository,local.document_id,local.branch,local.base_sha,local.commit_sha,planned.planned_commands,pr.stdout.strip() or None)
