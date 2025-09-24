from podcast_generator.fixtures import load_prompt_template
from podcast_generator.llm_models.openai import OpenAi
from podcast_generator.weave_op import weave_op


@weave_op()
def get_final_script(
    input: str,
) -> tuple[str, str]:
    model = OpenAi()

    prompt = load_prompt_template("final-script").format(
        input=input,
    )

    output = model.run(prompt)

    transcript, show_notes = output.split("\n---\n", 1)

    return transcript.strip(), show_notes.strip()
