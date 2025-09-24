import typer

from podcast_generator.pipeline.extract_draft import (
    extract_draft as extract_draft_core,
)


def extract_draft(
    input: typer.FileText = typer.Option(
        ...,
        help="The output of the previous stage containing the draft as well as some extraneous stuff",
    ),
    out: typer.FileTextWrite = typer.Option("-", help="Output file"),
):
    out.write(extract_draft_core(input.read()))
