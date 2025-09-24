import typer

from podcast_generator.cli.load_previous_episodes import load_previous_episodes
from podcast_generator.pipeline.get_feedback import (
    get_feedback as get_feedback_core,
)


def get_feedback(
    pi_dev_state: typer.FileText = typer.Option(
        None, help="JSON file containing pi.dev dump for repo"
    ),
    input: typer.FileText = typer.Option(
        ...,
        help="The output of the previous stage containing the draft",
    ),
    out: typer.FileTextWrite = typer.Option("-", help="Output file"),
):
    previous_episodes = load_previous_episodes(pi_dev_state)
    out.write(get_feedback_core(previous_episodes, input.read()))
