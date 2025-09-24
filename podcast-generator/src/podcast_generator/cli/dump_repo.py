import json
from datetime import UTC, datetime, timedelta

import typer
from rich.console import Console

from podcast_generator.github_personal_authorization import GithubPersonalAuthorization
from podcast_generator.pipeline.get_repo_data import get_repo_data

err_console = Console(stderr=True)

# GitHub GraphQL API endpoint
GRAPHQL_API_URL = "https://api.github.com/graphql"


def dump_repo(
    repository: str,
    pi_dev_state: typer.FileText = typer.Option(
        None, help="JSON file containing pi.dev dump for repo"
    ),
    since: datetime | None = typer.Option(
        None,
        formats=["%Y-%m-%dT%H:%M:%SZ"],
        help="Date to start from",
    ),
    until: datetime = typer.Option(
        datetime.now(UTC),
        formats=["%Y-%m-%dT%H:%M:%SZ"],
        help="Date to end at",
    ),
    out: typer.FileTextWrite = typer.Option("-", help="Output file"),
):
    owner, name = repository.split("/")

    pi_dev_state_data = json.loads(pi_dev_state.read()) if pi_dev_state else None

    if since is None:
        since = (
            datetime.fromisoformat(pi_dev_state_data["lastProcessedAt"])
            if pi_dev_state_data
            else until - timedelta(days=30)
        )

    data = get_repo_data(
        GithubPersonalAuthorization(),
        owner,
        name,
        since.astimezone(UTC),
        until.astimezone(UTC),
    )

    out.write(json.dumps(data, indent=2))
