from pathlib import Path

from podcast_generator.server.get_github_repo_id import get_github_repo_id


def get_run_artifacts_bucket_path(owner: str, name: str):
    return Path("runArtifacts") / get_github_repo_id(owner, name)
