import os
import tempfile
from io import BufferedRandom
from pathlib import Path

from podcast_generator.pipeline.generate_audio_segments import generate_audio_segments
from podcast_generator.pipeline.join_segments import join_segments


def generate_audio(transcript: str, output_file: BufferedRandom):
    with tempfile.TemporaryDirectory() as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        generate_audio_segments(
            transcript,
            tmp_dir,
            progress=False,
        )
        duration = join_segments(tmp_dir, output_file)

    length = output_file.seek(0, os.SEEK_END)

    print(f"Generated audio of length {length} bytes and duration {duration} seconds")
    return duration, length
