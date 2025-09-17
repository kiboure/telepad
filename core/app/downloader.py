from yt_dlp import YoutubeDL


class LargeSizeError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def get_filesize(url: str) -> int | None:
    ydl_opts = {
        "format": "bestaudio",
        "quiet": True,
        "noplaylist": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("filesize") or info.get("filesize_approx")


def download_and_convert(url: str, user_id: int, max_size: int = 5) -> str:
    filesize = get_filesize(url)
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
        "outtmpl": "%(user_id)s_%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return (ydl.prepare_filename(info).rsplit(".", 1)[0] + ".ogg", info.get("title"))
