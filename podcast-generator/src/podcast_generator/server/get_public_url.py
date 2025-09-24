import urllib.parse
from pathlib import Path

HOST = "https://pi.dev"


def get_public_url(path_raw: Path):
    path = urllib.parse.quote(str(path_raw))
    return f"{HOST}/{path}"
