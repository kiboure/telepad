# -- IMPORTS --
import os
import requests
import subprocess
from yt_dlp import YoutubeDL

from telepad.settings import MEDIA_ROOT

# -- ENV --
MAX_FILESIZE_MB = int(os.environ["MAX_FILESIZE_MB"])
BOT_STORAGE_ID = os.environ["BOT_STORAGE_ID"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice"

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
def download_and_convert(url: str, user_tg_id: int) -> str:
    info = get_metadata(url)
    filesize = get_filesize(info)
    if filesize and (filesize / 1024 / 1024) > MAX_FILESIZE_MB:
        raise LargeSizeError(f"Estimated file size exceeds {MAX_FILESIZE_MB}MB.")
    ydl_opts = {
        "format": "bestaudio",
        "max-filesize": f"{MAX_FILESIZE_MB*2}M",
        "restrictfilenames": True,
        "outtmpl": os.path.join(MEDIA_ROOT, f"temp_{user_tg_id}_%(title)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        temp_file = ydl.prepare_filename(info)

    name = os.path.splitext(os.path.basename(temp_file))[0]
    output_file = os.path.join(MEDIA_ROOT, f"{name}.ogg")

    command = [
        "ffmpeg",
        "-y",
        "-i", temp_file,
        "-vn",
        "-c:a", "libopus",
        "-b:a", "64k",
        "-vbr", "on",
        "-compression_level", "10",
        "-frame_duration", "60",
        "-application", "voip",
        output_file,
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)

    if temp_file and os.path.exists(temp_file):
        os.remove(temp_file)

    return (
        os.path.basename(output_file),
        info.get("title"),
        info.get("duration"),
    )


# -- TELEGRAM UPLOAD --
def upload_to_telegram(path: str, title: str, duration: int) -> str | None:
    with open(path, "rb") as voice_file:
        files = {"voice": (os.path.basename(path), voice_file, "audio/ogg")}
        data = {
            "chat_id": BOT_STORAGE_ID,
            "duration": duration,
            "filename": "".join(title.split()),
        }
        response = requests.post(API_URL, data=data, files=files, timeout=60)
        response.raise_for_status()

    if path and os.path.exists(path):
        os.remove(path)

    response = response.json()
    if response.get("ok"):
        return response["result"]["voice"]["file_id"]
    else:
        return {
            "status": "failed",
            "detail": str(response.get("description")),
        }
