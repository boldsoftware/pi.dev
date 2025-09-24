import typer

from podcast_generator.pipeline.get_final_script import get_final_script


def final_script(
    input: typer.FileText = typer.Option(
        ...,
        help="The output of the previous stage containing the final script",
    ),
    out_transcript: typer.FileTextWrite = typer.Option(
        "-", help="File to output plaintext transcript, to be run through TTS"
    ),
    out_show_notes: typer.FileTextWrite = typer.Option(
        "-", help="File to output show notes to"
    ),
):
    transcript, show_notes = get_final_script(input.read())

    out_transcript.write(transcript)
    out_show_notes.write(show_notes)
