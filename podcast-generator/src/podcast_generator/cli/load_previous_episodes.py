import json

import typer

from podcast_generator.EpisodeForPrompt import EpisodeForPrompt


def load_previous_episodes(pi_dev_state: typer.FileText) -> list[EpisodeForPrompt]:
    pi_dev_state_data = json.loads(pi_dev_state.read()) if pi_dev_state else None

    previous_episodes: list[EpisodeForPrompt] = (
        [
            {
                "createdAt": episode["createdAt"],
                "name": episode["name"],
                "description": episode["description"],
                "transcript": episode["transcript"],
                "since": episode["since"],
                "until": episode["until"],
            }
            for episode in pi_dev_state_data["episodes"]
        ]
        if pi_dev_state_data
        else []
    )

    return previous_episodes
