import hashlib
from pathlib import Path
from tempfile import mkdtemp
from typing import IO, Any

from google.cloud.storage import Bucket

from podcast_generator.server.get_logger import get_logger

logger = get_logger(__name__)


def upload_blob_from_string(
    bucket: Bucket,
    path: Path,
    contents: str,
    *,
    fail_if_exists=False,
    content_type="text/plain",
):
    """Uploads a file to the bucket."""
    bucket.blob(str(path)).upload_from_string(
        contents,
        if_generation_match=(0 if fail_if_exists else None),
        content_type=content_type,
    )


def upload_directory(bucket, directory_as_path_obj: Path, target_path: Path, workers=8):
    """Upload every file in a directory, including all files in subdirectories.

    Args:
        bucket: The GCS bucket to upload to
        source_directory: Local directory containing files to upload
        target_path: Path prefix in the bucket where files should be uploaded
        workers: Number of concurrent upload workers
    """
    source_directory = str(directory_as_path_obj)
    paths = directory_as_path_obj.rglob("*")
    file_paths = [path for path in paths if path.is_file()]
    relative_paths = [path.relative_to(source_directory) for path in file_paths]

    # Add target_path prefix to all paths
    string_paths = [str(path) for path in relative_paths]

    for local_path, rel_path in zip(file_paths, string_paths):
        try_count = 0
        while True:
            try:
                dest_path = f"{target_path}/{rel_path}"
                bucket.blob(dest_path).upload_from_filename(str(local_path))
                logger.info(f"Uploaded {rel_path} to {dest_path}")
            except Exception as e:
                try_count += 1
                if try_count >= 3:
                    logger.error(f"Failed to upload {rel_path} after 3 attempts: {e}")
                    raise e
            else:
                break


def upload_blob_from_file(
    bucket: Bucket, path: Path, file: IO[bytes], content_type: str = "text/plain"
):
    """Uploads a file to the bucket."""
    bucket.blob(str(path)).upload_from_file(
        file,
        content_type=content_type,
    )


def download_blob(bucket: Bucket, path: Path) -> Any:
    """Reads a file from the bucket."""
    return bucket.blob(str(path)).download_as_text()


cache: dict[str, Path] = {}
tmp_dir = Path(mkdtemp())


def download_with_cache(public_bucket: Bucket, name: str) -> Path:
    if name not in cache:
        # Create a hashed filename to avoid path/directory issues
        # while ensuring uniqueness for different assets
        hash_obj = hashlib.md5(name.encode())
        hashed_name = hash_obj.hexdigest()

        # Get the file extension if there is one
        _, ext = Path(name).name.rsplit(".", 1) if "." in Path(name).name else ("", "")
        filename = f"{hashed_name}.{ext}" if ext else hashed_name

        cache[name] = tmp_dir / filename
        public_bucket.blob(name).download_to_filename(str(cache[name]))
        logger.info(f"Downloaded {name} to {cache[name]}")
    return cache[name]
