import urllib.parse
from pathlib import Path
from typing import cast

from google.cloud.firestore import Client
from google.cloud.storage.bucket import Bucket

from podcast_generator.server.doc_schema import EpisodeDoc
from podcast_generator.server.gcs_utils import download_blob
from podcast_generator.server.get_logger import get_logger

logger = get_logger(__name__)


def fix_docs_core(
    db: Client,
    private_bucket: Bucket,
):
    snapshots = list(db.collection("repos").stream())

    for snapshot in snapshots:
        repo = snapshot.to_dict()
        if repo is None:
            continue
        for episode_snapshot in snapshot.reference.collection("episodes").stream():
            episode_doc = cast(EpisodeDoc, episode_snapshot.to_dict())
            if episode_doc is None:
                continue

            run = episode_doc["run"].get().to_dict()
            if run is None:
                continue

            root_artifacts_path = Path(urllib.parse.urlparse(run["artifacts"]).path[1:])
            artifacts_path = root_artifacts_path / "04-final-draft-raw.txt"

            print(f"Downloading {artifacts_path}...")

            transcript = download_blob(private_bucket, artifacts_path)
            episode_snapshot.reference.update({"transcript": transcript})
