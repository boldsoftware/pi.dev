import json

import typer

from podcast_generator.cli.load_previous_episodes import load_previous_episodes
from podcast_generator.pipeline.get_first_draft import get_first_draft


def first_draft(
    pi_dev_state: typer.FileText = typer.Option(
        None, help="JSON file containing pi.dev dump for repo"
    ),
    repository_data: typer.FileText = typer.Option(
        ..., help="JSON file containing repository data"
    ),
    out: typer.FileTextWrite = typer.Option("-", help="Output file"),
):
    repository_activity_json = json.loads(repository_data.read())

    previous_episodes = load_previous_episodes(pi_dev_state)

    out.write(get_first_draft(previous_episodes, repository_activity_json))
