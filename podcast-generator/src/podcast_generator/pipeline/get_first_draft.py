import json
from pathlib import Path

from podcast_generator.EpisodeForPrompt import EpisodeForPrompt
from podcast_generator.fixtures import (
    load_graphql_query,
    load_prompt,
    load_prompt_template,
)
from podcast_generator.llm_models.gemini import Gemini
from podcast_generator.weave_op import weave_op


@weave_op()
def get_first_draft(
    previous_episodes: list[EpisodeForPrompt],
    repository_data: dict,
) -> str:
    model = Gemini()

    context_template = load_prompt_template("context")
    prompt_template = load_prompt_template("first-draft")

    query = load_graphql_query("repository")

    with open(Path(__file__).parent / "get_repo_data.py") as file:
        python_script = file.read()

    guidelines = load_prompt("guidelines")

    prompt = prompt_template.format(
        context=context_template.format(
            query=query,
            python_script=python_script,
            previous_episodes=json.dumps(
                sorted(previous_episodes, key=lambda x: x["createdAt"])
            ),
            repository_activity=json.dumps(repository_data),
            repository=repository_data["repository"]["nameWithOwner"],
            guidelines=guidelines,
        )
    )

    return model.run(prompt)
