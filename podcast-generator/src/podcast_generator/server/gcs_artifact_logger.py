from pathlib import Path

from google.cloud.storage import Bucket

from podcast_generator.server.artifact_logger import ArtifactLogger
from podcast_generator.server.gcs_utils import (
    upload_blob_from_string,
    upload_directory,
)
from podcast_generator.server.get_logger import get_logger

logger = get_logger(__name__)


class GcsArtifactLogger(ArtifactLogger):
    def __init__(self, bucket: Bucket, base_path: Path):
        self.bucket = bucket
        self.base_path = base_path
        self.counter = 0

    def log(self, name: str, content: str):
        self.log_multiple([(name, content)])

    def _get_name_with_counter(self, name: str):
        return f"{self.counter:02}-{name}"

    def log_multiple(self, artifacts: list[tuple[str, str]]):
        for name, content in artifacts:
            name_with_counter = self._get_name_with_counter(name)
            logger.info(f"Generated artifact: {name_with_counter}")
            upload_blob_from_string(
                self.bucket,
                self.base_path / name_with_counter,
                content,
                fail_if_exists=True,
            )
        self.counter += 1

    def log_directory(self, name: str, directory: Path):
        name_with_counter = self._get_name_with_counter(name)
        logger.info(f"Generated artifact: {name_with_counter}")
        upload_directory(self.bucket, directory, self.base_path / name_with_counter)
        self.counter += 1
