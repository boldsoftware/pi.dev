import tempfile
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from google.cloud.firestore import Client
from google.cloud.storage import Bucket

from podcast_generator.generate_audio import generate_audio
from podcast_generator.server.episode import Episode
from podcast_generator.server.gcs_utils import upload_blob_from_file
from podcast_generator.server.get_logger import get_logger

logger = get_logger(__name__)

TRANSCRIPT = """\
Welcome to pi.dev, and congratulations on being the first person to
request a show for this repository! Our AI is now hard at work making
the first episode; check back in a few hours for the good stuff.
"""


def get_placeholder_episode_description(owner: str, name: str) -> str:
    return f"""\
Welcome to pi.dev, and congratulations on being the first person to
request a show for {owner}/{name}! Our AI is now hard at work making
the first episode; check back in a few hours for the good stuff.
"""


@dataclass
class PlaceholderEpisode:
    audioPublicUrl: str
    audio: str
    audioBytes: int
    audioDurationSeconds: int


place_holder_episode_base = None


def get_placeholder_episode_base(
    public_bucket: Bucket, db: Client
) -> PlaceholderEpisode:
    global place_holder_episode_base

    if place_holder_episode_base:
        return place_holder_episode_base

    doc = db.document("placeholderEpisode/placeholderEpisode")

    snapshot = doc.get()
    if snapshot.exists:
        place_holder_episode_base = PlaceholderEpisode(**cast(Any, snapshot.to_dict()))
        return place_holder_episode_base

    logger.info("Generating placeholder episode...")
    with tempfile.TemporaryFile() as tmp_file:
        duration, length = generate_audio(TRANSCRIPT, tmp_file)
        tmp_file.seek(0)
        upload_blob_from_file(
            public_bucket,
            Path("placeholder.mp3"),
            tmp_file,
        )

    place_holder_episode_base = PlaceholderEpisode(
        audioPublicUrl=f"https://storage.googleapis.com/{public_bucket.name}/placeholder.mp3",
        audio=f"gs://{public_bucket.name}/placeholder.mp3",
        audioBytes=length,
        audioDurationSeconds=duration,
    )

    doc.set(asdict(place_holder_episode_base))

    return place_holder_episode_base


def generate_placeholder_episode(
    public_bucket: Bucket, db: Client, owner: str, name: str
) -> Episode:
    base = get_placeholder_episode_base(public_bucket, db)

    return Episode(
        name=f"Welcome to {owner}/{name} by pi.dev!",
        publication_date=datetime.now(UTC),
        description=get_placeholder_episode_description(owner, name),
        url=base.audioPublicUrl,
        length=base.audioBytes,
        duration=base.audioDurationSeconds,
        guid=uuid.uuid4().hex,
    )
