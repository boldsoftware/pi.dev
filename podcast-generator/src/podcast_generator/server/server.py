import os
from datetime import UTC, datetime
from enum import Enum
from typing import cast

import firebase_admin
import requests
from firebase_admin import firestore
from flask import Flask, abort, jsonify
from google.cloud import storage
from google.cloud.firestore import Query

from podcast_generator.github_app_authorization import GithubAppAuthorization
from podcast_generator.github_personal_authorization import GithubPersonalAuthorization
from podcast_generator.server.doc_schema import EpisodeDoc
from podcast_generator.server.environment import is_prod
from podcast_generator.server.fix_docs_core import fix_docs_core
from podcast_generator.server.generate_rss_feed import update_rss_feed
from podcast_generator.server.get_github_doc_ref import get_github_doc_ref
from podcast_generator.server.get_logger import get_logger
from podcast_generator.server.get_public_url import get_public_url
from podcast_generator.server.get_shows_gcs_path import (
    get_feed_gcs_path,
    get_show_logo_public_url,
)
from podcast_generator.server.get_stuck_repos_core import stuck_repos_core
from podcast_generator.server.lock import LockHeldError, acquire_lock
from podcast_generator.server.update_podcasts_core import update_podcasts_core
from podcast_generator.server.validate_and_canonicalize_repo import (
    validate_and_canonicalize_repo,
)

app = Flask(__name__)


logger = get_logger(__name__)

github_auth = GithubAppAuthorization() if is_prod() else GithubPersonalAuthorization()
db = firestore.client(firebase_admin.initialize_app())


class UpdateStatus(str, Enum):
    COMPLETED = "COMPLETED"
    ALREADY_IN_PROGRESS = "ALREADY_IN_PROGRESS"


@app.route("/update", methods=["POST"])
def update_podcasts():
    logger.info("Updating podcasts...")
    public_bucket_name = os.environ["PUBLIC_BUCKET_NAME"]
    private_bucket_name = os.environ["PRIVATE_BUCKET_NAME"]

    try:
        with acquire_lock(private_bucket_name, "lock"):
            storage_client = storage.Client()
            private_bucket = storage_client.bucket(private_bucket_name)
            public_bucket = storage_client.bucket(public_bucket_name)

            update_podcasts_core(db, github_auth, private_bucket, public_bucket)

            logger.info("Done updating podcasts.")
            return jsonify({"status": UpdateStatus.COMPLETED.value})
    except LockHeldError:
        logger.info("Podcasts generation already in progress.")
        return jsonify({"status": UpdateStatus.ALREADY_IN_PROGRESS.value})


@app.route("/fix-docs", methods=["POST"])
def fix_docs():
    """
    Utility function to bulk-update docs. Currently only used to fix missing transcripts,
    but code is kept around in case useful for other one-off tasks.
    """
    logger.info("Fixing docs...")
    private_bucket_name = os.environ["PRIVATE_BUCKET_NAME"]

    try:
        with acquire_lock(private_bucket_name, "lock"):
            storage_client = storage.Client()
            private_bucket = storage_client.bucket(private_bucket_name)

            fix_docs_core(db, private_bucket)

            logger.info("Done fixing docs.")
            return jsonify({"status": UpdateStatus.COMPLETED.value})
    except LockHeldError:
        logger.info("Podcasts generation already in progress.")
        return jsonify({"status": UpdateStatus.ALREADY_IN_PROGRESS.value})


class RequestRepoStatus(str, Enum):
    REQUESTED = "REQUESTED"
    ALREADY_REQUESTED = "ALREADY_REQUESTED"
    REDIRECT = "REDIRECT"


@app.route("/request/github.com/<owner>/<name>", methods=["POST"])
def request_repo(owner: str, name: str):
    public_bucket_name = os.environ["PUBLIC_BUCKET_NAME"]
    public_bucket = storage.Client().bucket(public_bucket_name)

    try:
        canonical_owner, canonical_name = validate_and_canonicalize_repo(
            github_auth, owner, name
        )
    except requests.HTTPError:
        abort(404, description="Repository is not valid")

    if canonical_owner != owner or canonical_name != name:
        return jsonify(
            {
                "status": RequestRepoStatus.REDIRECT.value,
                "owner": canonical_owner,
                "name": canonical_name,
            }
        )

    doc_ref = get_github_doc_ref(db, owner, name)
    feed_url = get_feed_url(owner, name)

    if doc_ref.get().exists:
        return jsonify(
            {"status": RequestRepoStatus.ALREADY_REQUESTED.value, "feedUrl": feed_url}
        )

    update_rss_feed(
        public_bucket,
        db,
        owner,
        name,
    )

    doc_ref.set(
        {
            "host": "github.com",
            "owner": owner,
            "name": name,
            "requestedAt": datetime.now(UTC),
            "lastProcessedAt": datetime.min,
            "tryCount": 0,
            "feedUrl": feed_url,
        }
    )

    return jsonify(
        {
            "status": RequestRepoStatus.REQUESTED.value,
            "feedUrl": feed_url,
            "logoUrl": get_show_logo_public_url(public_bucket, owner, name),
        }
    )


@app.route("/force-regen-rss/github.com/<owner>/<name>", methods=["POST"])
def force_regen_rss(owner: str, name: str):
    public_bucket_name = os.environ["PUBLIC_BUCKET_NAME"]
    public_bucket = storage.Client().bucket(public_bucket_name)

    doc_ref = get_github_doc_ref(db, owner, name)
    if not doc_ref.get().exists:
        abort(404, description="Repository has not been requested")

    update_rss_feed(
        public_bucket,
        db,
        owner,
        name,
    )

    return jsonify({"feedUrl": get_feed_url(owner, name)})


@app.route("/force-regen-all-rss", methods=["POST"])
def force_regen_all_rss():
    public_bucket_name = os.environ["PUBLIC_BUCKET_NAME"]
    public_bucket = storage.Client().bucket(public_bucket_name)

    try:
        with acquire_lock(public_bucket_name, "lock"):
            for snapshot in db.collection("repos").stream():
                repo = snapshot.to_dict()
                if repo is None:
                    continue
                owner = repo["owner"]
                name = repo["name"]
                update_rss_feed(
                    public_bucket,
                    db,
                    owner,
                    name,
                    regenerate_logo=True,
                )
                logger.info(f"Updated RSS feed for {owner}/{name}")

            return jsonify({"status": UpdateStatus.COMPLETED.value})
    except LockHeldError:
        logger.info("Podcasts generation already in progress.")
        return jsonify({"status": UpdateStatus.ALREADY_IN_PROGRESS.value})


@app.route("/github.com/<owner>/<name>.json")
def dump(owner: str, name: str):
    doc_ref = get_github_doc_ref(db, owner, name)

    snapshot = doc_ref.get()
    if not snapshot.exists:
        abort(404, description="Repository has not been requested")

    doc = cast(dict, snapshot.to_dict())

    return jsonify(
        {
            "host": doc["host"],
            "owner": doc["owner"],
            "name": doc["name"],
            "requestedAt": doc["requestedAt"].isoformat(),
            "lastProcessedAt": doc["lastProcessedAt"].isoformat(),
            "episodes": [
                episode_to_dict(episode.to_dict())
                for episode in doc_ref.collection("episodes")
                .order_by("createdAt", direction=Query.DESCENDING)
                .stream()
            ],
        }
    )


def episode_to_dict(episode: EpisodeDoc):
    return {
        "name": episode["name"],
        "guid": episode["guid"],
        "createdAt": episode["createdAt"].isoformat(),
        "since": episode["since"].isoformat(),
        "until": episode["until"].isoformat(),
        "description": episode["description"],
        "transcript": episode["transcript"],
        "audioPublicUrl": episode["audioPublicUrl"],
        "audioDurationSeconds": episode["audioDurationSeconds"],
    }


def get_feed_url(owner: str, name: str):
    return get_public_url(get_feed_gcs_path(owner, name))


@app.route("/reset-try-count/github.com/<owner>/<name>", methods=["POST"])
def reset_try_count(owner: str, name: str):
    doc_ref = get_github_doc_ref(db, owner, name)

    if not doc_ref.get().exists:
        abort(404, description="Repository has not been requested")

    doc_ref.update({"tryCount": 0})

    return jsonify({"status": "SUCCESS"})


@app.route("/stuck-repos", methods=["GET"])
def stuck_repos():
    return jsonify(stuck_repos_core(db))


if __name__ == "__main__":
    app.run(debug=True)
