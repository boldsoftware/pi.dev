from datetime import datetime
from typing import TypedDict

from google.cloud.firestore import DocumentReference


class EpisodeDoc(TypedDict):
    name: str
    guid: str
    run: DocumentReference
    createdAt: datetime

    since: datetime
    until: datetime

    description: str
    transcript: str

    audio: str
    audioPublicUrl: str
    audioBytes: int
    audioDurationSeconds: float
