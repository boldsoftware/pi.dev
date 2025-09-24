from pathlib import Path

import typer

from podcast_generator.pipeline.generate_audio_segments import (
    generate_audio_segments as generate_audio_core,
)


def generate_audio(
    input: typer.FileText = typer.Option(
        ...,
        help="The script",
    ),
    out_dir: Path = typer.Option(
        ...,
        help="Output directory",
    ),
):
    generate_audio_core(input.read(), out_dir, progress=True)
