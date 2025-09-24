from podcast_generator.fixtures import load_prompt_template
from podcast_generator.llm_models.claude import Claude, ClaudeModel
from podcast_generator.weave_op import weave_op


@weave_op()
def extract_draft(
    input: str,
) -> str:
    model = Claude(model_name=ClaudeModel.HAIKU, temperature=0.0)

    prompt = load_prompt_template("extract-draft").format(
        input=input,
    )

    return model.run(prompt)
