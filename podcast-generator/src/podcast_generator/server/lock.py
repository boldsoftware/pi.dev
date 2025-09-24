import os
from contextlib import contextmanager
from datetime import datetime, timedelta

import google.api_core.exceptions
from google.cloud import storage

# Process can hold lock until it's 10 seconds past when GCP kills it
lock_ttl = timedelta(seconds=int(os.environ["TIMEOUT_SECONDS"]) + 10)


@contextmanager
def acquire_lock(bucket_name: str, path: str):
    """
    Acquire a lock using a GCS blob, relying on the generation number to prevent
    simultaneous access.

    If the lock is older than 30 minutes, it will be deleted and an exception
    will be raised.

    Args:
        bucket_name (str): The name of the GCS bucket
        path (str): The path to the blob

    Raises:
        LockHeldError: If the lock is already held
        StaleLockError: If the lock is stale
    """
    my_generation: int | None = None
    lock_held = False

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(path)

    try:
        blob.upload_from_string("locked", if_generation_match=0)
        my_generation = blob.generation
        lock_held = True

        yield
    except google.api_core.exceptions.PreconditionFailed:
        blob.reload()
        generation = blob.generation
        lock_creation_time = blob.time_created

        if (
            lock_creation_time is not None
            and lock_creation_time
            < datetime.now(tz=lock_creation_time.tzinfo) - lock_ttl
        ):
            # If the lock is older than 30 minutes, delete it and raise an error.
            # The next run will be able to acquire the lock
            blob.delete(if_generation_match=generation)
            print("Lock is stale; deleted.")
            raise StaleLockError(lock_ttl)

        raise LockHeldError()
    finally:
        if lock_held:
            blob.delete(if_generation_match=my_generation)


class LockHeldError(Exception):
    pass


class StaleLockError(Exception):
    def __init__(self, lock_age: timedelta):
        self.lock_age = lock_age
        super().__init__(f"Lock is older than {lock_age}.")
