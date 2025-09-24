from pathlib import Path

import typer

from podcast_generator.pipeline.join_segments import join_segments as join_segments_core


def join_segments(
    in_dir: Path = typer.Option(
        ...,
        help="Input directory containing the audio segments to join",
    ),
    out: typer.FileBinaryWrite = typer.Option(..., help="Output file"),
):
    join_segments_core(in_dir, out)
