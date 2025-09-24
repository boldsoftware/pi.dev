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
def apply_feedback(
    previous_episodes: list[EpisodeForPrompt],
    repository_data: dict,
    draft: str,
    feedback: str,
):
    model = Gemini(temperature=0.0)

    context_template = load_prompt_template("context")
    prompt_template = load_prompt_template("apply-feedback")
    guidelines = load_prompt("guidelines")
    query = load_graphql_query("repository")

    with open(Path(__file__).parent / "get_repo_data.py") as file:
        python_script = file.read()

    prompt = prompt_template.format(
        context=context_template.format(
            query=query,
            python_script=python_script,
            repository_activity=json.dumps(repository_data),
            previous_episodes=json.dumps(
                sorted(previous_episodes, key=lambda x: x["createdAt"])
            ),
            repository=repository_data["repository"]["nameWithOwner"],
            guidelines=guidelines,
        ),
        draft=draft,
        feedback=feedback,
    )

    return model.run(prompt)
