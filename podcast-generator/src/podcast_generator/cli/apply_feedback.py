import json

import typer

from podcast_generator.cli.load_previous_episodes import load_previous_episodes
from podcast_generator.pipeline.apply_feedback import (
    apply_feedback as apply_feedback_core,
)


def apply_feedback(
    pi_dev_state: typer.FileText = typer.Option(
        None, help="JSON file containing pi.dev dump for repo"
    ),
    repository_data: typer.FileText = typer.Option(
        ..., help="JSON file containing repository data"
    ),
    draft: typer.FileText = typer.Option(
        ...,
        help="The draft to apply feedback to",
    ),
    feedback: typer.FileText = typer.Option(
        ...,
        help="The feedback to apply",
    ),
    out: typer.FileTextWrite = typer.Option("-", help="Output file"),
):
    repository_activity_json = json.loads(repository_data.read())

    out.write(
        apply_feedback_core(
            load_previous_episodes(pi_dev_state),
            repository_activity_json,
            draft.read(),
            feedback.read(),
        )
    )
