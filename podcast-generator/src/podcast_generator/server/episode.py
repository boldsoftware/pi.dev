from dataclasses import dataclass
from datetime import datetime

from podcast_generator.server.doc_schema import EpisodeDoc


@dataclass
class Episode:
    name: str
    publication_date: datetime
    description: str
    url: str
    length: int
    duration: float
    guid: str

    @staticmethod
    def from_doc(doc: EpisodeDoc):
        return Episode(
            name=doc["name"],
            publication_date=doc["createdAt"],
            description=doc["description"],
            url=doc["audioPublicUrl"],
            length=doc["audioBytes"],
            duration=doc["audioDurationSeconds"],
            guid=doc["guid"],
        )
