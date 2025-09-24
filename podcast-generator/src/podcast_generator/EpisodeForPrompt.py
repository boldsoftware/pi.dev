from typing import TypedDict

from podcast_generator.server.doc_schema import EpisodeDoc


class EpisodeForPrompt(TypedDict):
    name: str
    createdAt: str

    since: str
    until: str

    description: str
    transcript: str


def get_episode_for_prompt(episode: EpisodeDoc) -> EpisodeForPrompt:
    return {
        "name": episode["name"],
        "createdAt": episode["createdAt"].isoformat(),
        "since": episode["since"].isoformat(),
        "until": episode["until"].isoformat(),
        "description": episode["description"],
        "transcript": episode["transcript"],
    }
