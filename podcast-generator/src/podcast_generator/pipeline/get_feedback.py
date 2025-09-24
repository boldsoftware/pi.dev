import json

from podcast_generator.EpisodeForPrompt import EpisodeForPrompt
from podcast_generator.fixtures import load_prompt, load_prompt_template
from podcast_generator.llm_models.claude import Claude
from podcast_generator.weave_op import weave_op


@weave_op()
def get_feedback(
    previous_episodes: list[EpisodeForPrompt],
    input: str,
) -> str:
    model = Claude()

    prompt_template = load_prompt_template("get-feedback")
    guidelines = load_prompt("guidelines")

    prompt = prompt_template.format(
        draft=input,
        guidelines=guidelines,
        previous_episodes=json.dumps(
            sorted(previous_episodes, key=lambda x: x["createdAt"])
        ),
    )

    return model.run(prompt)
