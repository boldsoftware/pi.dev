from datetime import UTC, datetime
from typing import cast

from google.cloud.firestore import Client, DocumentReference, FieldFilter, Increment
from google.cloud.storage.bucket import Bucket

from podcast_generator.github_authorization import GithubAuthorization
from podcast_generator.server.create_episode import create_episode
from podcast_generator.server.episode_config import EPISODE_SPACING
from podcast_generator.server.generate_rss_feed import update_rss_feed
from podcast_generator.server.get_logger import get_logger
from podcast_generator.server.is_datetime_min import is_datetime_min
from podcast_generator.server.server_config import MAX_REPOS_PER_RUN, MAX_TRY_COUNT

logger = get_logger(__name__)


def update_podcasts_core(
    db: Client,
    github_auth: GithubAuthorization,
    private_bucket: Bucket,
    public_bucket: Bucket,
):
    snapshots = list(
        db.collection("repos")
        .where(
            filter=FieldFilter(
                "lastProcessedAt",
                "<",
                (datetime.now(UTC) - EPISODE_SPACING),
            )
        )
        .where(
            filter=FieldFilter(
                "tryCount",
                "<",
                MAX_TRY_COUNT,
            )
        )
        .limit(MAX_REPOS_PER_RUN)
        .stream()
    )

    for snapshot in snapshots:
        repo = snapshot.to_dict()
        if repo is None:
            continue
        updated_db = False
        try:
            last_processed = repo["lastProcessedAt"]
            owner, name = repo["owner"], repo["name"]

            if is_datetime_min(last_processed):
                last_processed = None

            match repo["host"]:
                case "github.com":
                    episode_doc = create_episode(
                        private_bucket,
                        github_auth,
                        snapshot.reference,
                        public_bucket,
                        owner,
                        name,
                        last_processed,
                    )
                case _:
                    raise ValueError(f"Unknown host: {repo['host']}")

            episode_doc_ref: DocumentReference = snapshot.reference.collection(
                "episodes"
            ).document(episode_doc["name"])
            batch = db.batch()
            batch.set(episode_doc_ref, cast(dict, episode_doc))
            batch.update(
                snapshot.reference,
                {"lastProcessedAt": episode_doc["until"], "tryCount": 0},
            )
            batch.commit()
            updated_db = True

            # Unfortunately we can't atomically update bucket and firestore, so
            # we update firestore first. If we fail to update the rss feed, we'll
            # just have to redo it manually
            update_rss_feed(public_bucket, db, owner, name)

            logger.info(f"Completed processing {owner}/{name}")
        except Exception as e:
            try_count = repo["tryCount"] + 1
            snapshot.reference.update({"tryCount": Increment(1)})
            json_payload = {
                "error": str(e),
                "repo": snapshot.id,
                "tryCount": try_count,
            }

            logger.exception(e, extra={"json_fields": json_payload})

            if try_count >= MAX_TRY_COUNT:
                logger.critical(
                    "Exceeded maximum number of tries",
                    extra={"json_fields": json_payload},
                )

            if updated_db:
                # FIXME: Actually handle this case; for now we just log it
                # so we can manually fix it
                logger.critical(
                    "Updated db but not RSS feed",
                    extra={"json_fields": json_payload},
                )
