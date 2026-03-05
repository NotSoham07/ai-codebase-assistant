from __future__ import annotations
import os
import hashlib
from git import Repo
from app.settings import settings

def repo_id_for_url(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]

def repo_dir(repo_id: str) -> str:
    return os.path.join(settings.data_dir, "repos", repo_id)

def ensure_repo_cloned(repo_url: str, branch: str | None) -> str:
    rid = repo_id_for_url(repo_url)
    path = repo_dir(rid)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path) and os.path.isdir(os.path.join(path, ".git")):
        repo = Repo(path)
        repo.remotes.origin.fetch(prune=True)
        if branch:
            repo.git.checkout(branch)
            repo.remotes.origin.pull()
        else:
            # pull current branch
            repo.remotes.origin.pull()
        return rid

    repo = Repo.clone_from(repo_url, path)
    if branch:
        repo.git.checkout(branch)
    return rid

def list_repos() -> list[dict]:
    base = os.path.join(settings.data_dir, "indexes")
    if not os.path.exists(base):
        return []
    out = []
    for rid in sorted(os.listdir(base)):
        out.append({"repo_id": rid})
    return out