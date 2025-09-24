import json
import tempfile
from dataclasses import dataclass
from datetime import datetime
from io import BufferedRandom
from pathlib import Path

from podcast_generator.EpisodeForPrompt import EpisodeForPrompt
from podcast_generator.github_authorization import GithubAuthorization
from podcast_generator.pipeline.apply_feedback import apply_feedback
from podcast_generator.pipeline.extract_draft import extract_draft
from podcast_generator.pipeline.generate_audio_segments import generate_audio_segments
from podcast_generator.pipeline.get_feedback import get_feedback
from podcast_generator.pipeline.get_final_script import get_final_script
from podcast_generator.pipeline.get_first_draft import get_first_draft
from podcast_generator.pipeline.get_repo_data import get_repo_data
from podcast_generator.pipeline.join_segments import join_segments
from podcast_generator.server.artifact_logger import ArtifactLogger
from podcast_generator.weave_op import weave_op


@dataclass
class PipelineOutput:
    duration: float
    show_notes: str
    transcript: str


@weave_op()
def run_pipeline(
    artifact_logger: ArtifactLogger,
    github_auth: GithubAuthorization,
    owner: str,
    name: str,
    since: datetime,
    until: datetime,
    previous_episodes: list[EpisodeForPrompt],
    audio_output_file: BufferedRandom,
):
    repo_dump = get_repo_data(
        github_auth,
        owner,
        name,
        since,
        until,
    )
    artifact_logger.log("repo-data.json", json.dumps(repo_dump))

    first_draft_raw = get_first_draft(previous_episodes, repo_dump)
    artifact_logger.log("first-draft-raw.txt", first_draft_raw)

    first_draft = extract_draft(first_draft_raw)
    artifact_logger.log("first-draft.txt", first_draft)

    feedback = get_feedback(previous_episodes, first_draft)
    artifact_logger.log("feedback.txt", feedback)

    final_draft_raw = apply_feedback(
        previous_episodes, repo_dump, first_draft, feedback
    )
    artifact_logger.log("final-draft-raw.txt", final_draft_raw)

    transcript, show_notes = get_final_script(final_draft_raw)
    artifact_logger.log_multiple(
        [("transcript.txt", transcript), ("show-notes.txt", show_notes)]
    )

    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        generate_audio_segments(
            transcript,
            tmp_dir,
            progress=False,
        )
        artifact_logger.log_directory("audio-segments", tmp_dir)

        duration = join_segments(tmp_dir, audio_output_file)

    return PipelineOutput(
        duration=duration, show_notes=show_notes, transcript=final_draft_raw
    )
