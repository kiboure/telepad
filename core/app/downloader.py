# -- IMPORTS --
import os
from yt_dlp import YoutubeDL

from telepad.settings import MEDIA_ROOT


# -- HELPERS --
class LargeSizeError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def get_metadata(url: str) -> dict:
    ydl_opts = {
        "format": "bestaudio",
        "quiet": True,
        "noplaylist": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info


def get_filesize(info: dict) -> int | None:
    return info.get("filesize") or info.get("filesize_approx")


# -- DOWNLOADER --
def download_and_convert(url: str, user_id: int, max_size: int = 5) -> str:
    info = get_metadata(url)
    # Could check for file existence here; ydl.prepare_filename(info).rsplit(".", 1)[0]
    filesize = get_filesize(info)
    if filesize and (filesize / 1024 / 1024) > max_size:
        raise LargeSizeError(f"Estimated file size exceeds {max_size}MB.")

    ydl_opts = {
        "format": "bestaudio",
        "extractaudio": True,
        "restrictfilenames": True,
        "audioformat": "ogg",
        "prefer_ffmpeg": True,
        "postprocessor_args": [
            "-c:a",
            "libopus",
            "-b:a",
            "48k",
            "-ar",
            "48000",
            "-ac",
            "1",
        ],
        "outtmpl": os.path.join(MEDIA_ROOT, f"{user_id}_%(title)s.ogg"),
        "quiet": True,
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return (
            ydl.prepare_filename(info).rsplit("/", 1)[1],
            info.get("title"),
        )
