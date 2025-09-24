from pathlib import Path

import weave

from podcast_generator.hidden_prints import HiddenPrints

root_dir = Path(__file__).parent.parent.parent


def load_graphql_query(name: str) -> str:
    with open(root_dir / "queries" / f"{name}.graphql") as f:
        return f.read()


class Prompt:
    def __init__(self, content: str):
        self.wandb_prompt = weave.StringPrompt(content)

    def format(self, **kwargs) -> str:
        return self.wandb_prompt.format(**kwargs)


def load_prompt_template(name: str) -> Prompt:
    with open(root_dir / "prompts" / f"{name}.txt") as file:
        prompt = Prompt(file.read())
        # This is a hack to prevent annoying weave logging. See
        # https://github.com/wandb/weave/issues/3426
        with HiddenPrints():
            weave.publish(prompt.wandb_prompt, name=name)
        return prompt


def load_prompt(name: str) -> str:
    return load_prompt_template(name).format()
