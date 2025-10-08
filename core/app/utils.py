# -- IMPORTS --
import os
import requests
import subprocess
from yt_dlp import YoutubeDL

# -- ENV --
from telepad.settings import MEDIA_ROOT

MAX_FILESIZE_MB = int(os.environ["MAX_FILESIZE_MB"])
BOT_STORAGE_ID = os.environ["BOT_STORAGE_ID"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice"


# -- EXCEPTIONS --
class LargeSizeError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# -- HELPERS --
def ydl_get_metadata(url: str) -> dict:
    ydl_opts = {
        "format": "bestaudio/bestvideo/best",
        "quiet": True,
        "noplaylist": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info


def ffprobe_get_duration(filepath: str):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        filepath,
    ]

    output = subprocess.run(command, check=True, capture_output=True, text=True)
    duration = int(float(output.stdout.strip()))

    return duration


# -- UTILS --
def ydl_download(url: str, user_id: int) -> str:
    info = ydl_get_metadata(url)
    filesize = info.get("filesize") or info.get("filesize_approx")
    if filesize and (filesize / 1024 / 1024) > MAX_FILESIZE_MB:
        raise LargeSizeError(f"Estimated file size exceeds {MAX_FILESIZE_MB}MB.")

    ydl_opts = {
        "format": "bestaudio/bestvideo/best",
        "max-filesize": f"{MAX_FILESIZE_MB * 2}M",
        "restrictfilenames": True,
        "outtmpl": os.path.join(MEDIA_ROOT, f"temp/{user_id}_%(title)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file = ydl.prepare_filename(info)

    return file, info


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


def convert(input_file: str, output_file: str):
    command = [
        "ffmpeg",
        "-y",
        "-i", input_file,
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

    if input_file and os.path.exists(input_file):
        os.remove(input_file)
