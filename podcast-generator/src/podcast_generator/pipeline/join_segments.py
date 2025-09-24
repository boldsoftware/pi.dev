from pathlib import Path
from typing import IO

from pydub import AudioSegment


def join_segments(
    in_dir: Path,
    out_file: Path | IO[bytes],
):
    # Iterate over the files in the input directory
    segments = [
        AudioSegment.from_file(file)
        for file in sorted(in_dir.iterdir())
        if file.is_file()
    ]

    # Merge all the chunks into a single file
    output = segments[0]
    for segment in segments[1:]:
        output = output + AudioSegment.silent(duration=1000) + segment

    output.export(out_file, format="mp3")

    return output.duration_seconds
