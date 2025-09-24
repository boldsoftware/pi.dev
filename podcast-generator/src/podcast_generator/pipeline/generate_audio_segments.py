from pathlib import Path

from openai import OpenAI
from tqdm import tqdm

from podcast_generator.weave_op import weave_op


@weave_op()
def generate_audio_segments(
    input: str,
    out_dir: Path,
    *,
    progress: bool,
):
    out_dir.mkdir(parents=True, exist_ok=True)
    client = OpenAI()

    chunks = list(get_chunks(input))
    if progress:
        chunks = tqdm(chunks)
    for index, chunk in enumerate(chunks):
        output_chunk_path = out_dir / f"chunk{index:02d}.mp3"
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="alloy",
            input=chunk,
        )

        response.write_to_file(output_chunk_path)


def get_chunks(text: str, max_length=4096):
    """
    Split text into chunks of at most `max_length` characters. Text is first split
    on markdown paragraph boundaries (`\n\n`). We refuse to split a paragraph across
    chunks, so we output as many paragraphs as will fit in a chunk, joined by `\n\n`,
    and then continue with the next chunk.
    """
    paragraphs = text.split("\n\n")
    chunk = ""
    for paragraph in paragraphs:
        if len(chunk) + len(paragraph) + 2 > max_length:
            yield chunk
            chunk = ""
        chunk += paragraph + "\n\n"
    yield chunk
