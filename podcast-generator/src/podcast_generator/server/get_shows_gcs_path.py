from pathlib import Path

from google.cloud.storage.bucket import Bucket

from podcast_generator.server.get_github_repo_id import get_github_repo_id


def get_shows_gcs_path(owner, name):
    return Path("shows") / get_github_repo_id(owner, name)


def get_feed_gcs_path(owner, name):
    return get_shows_gcs_path(owner, name) / "podcast.rss"


def get_show_logo_path(owner, name):
    return get_shows_gcs_path(owner, name) / "logo.webp"


def get_show_logo_public_url(public_bucket: Bucket, owner: str, name: str):
    return public_bucket.blob(str(get_show_logo_path(owner, name))).public_url
