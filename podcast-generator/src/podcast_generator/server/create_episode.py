import os
import tempfile
import uuid
from datetime import UTC, datetime
from io import BufferedRandom
from pathlib import Path

import weave
from google.cloud.firestore import DocumentReference
from google.cloud.storage import Bucket

from podcast_generator.EpisodeForPrompt import get_episode_for_prompt
from podcast_generator.github_authorization import GithubAuthorization
from podcast_generator.pipeline.run_pipeline import run_pipeline
from podcast_generator.server.doc_schema import EpisodeDoc
from podcast_generator.server.environment import env
from podcast_generator.server.episode_config import EPISODE_SPACING
from podcast_generator.server.gcs_artifact_logger import GcsArtifactLogger
from podcast_generator.server.gcs_utils import upload_blob_from_file
from podcast_generator.server.get_logger import get_logger
from podcast_generator.server.get_public_url import get_public_url
from podcast_generator.server.get_run_artifacts_bucket_path import (
    get_run_artifacts_bucket_path,
)
from podcast_generator.server.get_shows_gcs_path import get_shows_gcs_path

logger = get_logger(__name__)

commit_sha = os.environ["COMMIT_SHA"]


def create_episode(
    private_bucket: Bucket,
    github_auth: GithubAuthorization,
    repo_doc_ref: DocumentReference,
    public_bucket: Bucket,
    owner: str,
    name: str,
    last_processed: datetime | None,
):
    logger.info(f"Processing {owner}/{name}...")

    since = last_processed or datetime.now(UTC) - EPISODE_SPACING
    until = datetime.now(UTC)

    run_artifacts_bucket_path = get_run_artifacts_bucket_path(owner, name)

    run_id = uuid.uuid4().hex
    logger.info(f"Run ID: {run_id}")

    run_path = run_artifacts_bucket_path / run_id
    run_doc_ref: DocumentReference = repo_doc_ref.collection("runs").document(run_id)

    try:
        run_doc_ref.set(
            {
                "commitSha": commit_sha,
                "startedProcessingAt": datetime.now(UTC),
                "since": since,
                "until": until,
                "artifacts": f"gs://{private_bucket.name}/{run_path}",
            }
        )

        previous_episodes = [
            get_episode_for_prompt(episode.to_dict())
            for episode in repo_doc_ref.collection("episodes").stream()
        ]

        artifact_logger = GcsArtifactLogger(private_bucket, run_path)

        with (
            tempfile.TemporaryFile() as audio_tmp_file,
            weave.attributes({"env": env(), "run_id": run_id}),
        ):
            outputs = run_pipeline(
                artifact_logger=artifact_logger,
                github_auth=github_auth,
                owner=owner,
                name=name,
                since=since,
                until=until,
                previous_episodes=previous_episodes,
                audio_output_file=audio_tmp_file,
            )

            run_doc_ref.update(
                {
                    "completedProcessingAt": datetime.now(UTC),
                }
            )

            episode_name = datetime.now(UTC).strftime("%Y-%m-%d")

            episode_audio_path = get_shows_gcs_path(owner, name) / f"{run_id}.mp3"
            episode_audio_size = audio_tmp_file.seek(0, os.SEEK_END)

            upload_blob_from_buffered_random(
                public_bucket, episode_audio_path, audio_tmp_file, "audio/mpeg"
            )

            audio_public_url = get_public_url(episode_audio_path)
            audio_full_gcs_path = f"gs://{public_bucket.name}/{episode_audio_path}"

            logger.info(f"Uploaded episode audio to {audio_full_gcs_path}")

        episode_doc: EpisodeDoc = {
            "name": episode_name,
            "guid": run_id,
            "run": run_doc_ref,
            "createdAt": datetime.now(UTC),
            "since": since,
            "until": until,
            "description": outputs.show_notes,
            "transcript": outputs.transcript,
            "audio": audio_full_gcs_path,
            "audioPublicUrl": audio_public_url,
            "audioBytes": episode_audio_size,
            "audioDurationSeconds": outputs.duration,
        }

        return episode_doc
    except Exception as e:
        run_doc_ref.update(
            {
                "error": str(e),
                "errorAt": datetime.now(UTC),
            }
        )
        raise e


def upload_blob_from_buffered_random(
    public_bucket: Bucket, path: Path, f: BufferedRandom, content_type: str
):
    f.seek(0)

    upload_blob_from_file(
        public_bucket,
        path,
        f,
        content_type=content_type,
    )
