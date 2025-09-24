import typer

from podcast_generator.cli.apply_feedback import apply_feedback
from podcast_generator.cli.dump_repo import dump_repo
from podcast_generator.cli.extract_draft import extract_draft
from podcast_generator.cli.final_script import final_script
from podcast_generator.cli.first_draft import first_draft
from podcast_generator.cli.generate_audio import generate_audio
from podcast_generator.cli.get_feedback import get_feedback
from podcast_generator.cli.join_segments import join_segments

app = typer.Typer()

# Add dump_repo command
app.command()(dump_repo)
app.command()(first_draft)
app.command()(extract_draft)
app.command()(get_feedback)
app.command()(apply_feedback)
app.command()(final_script)
app.command()(generate_audio)
app.command()(join_segments)

if __name__ == "__main__":
    app()
