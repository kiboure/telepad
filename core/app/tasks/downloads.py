import os
import subprocess
import logging
from celery import shared_task
from app.models import Sound
from app.downloader import download_and_convert
from users.models import User


@shared_task
def download_sound(user_id: int, url: str):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return {"detail": "User not found."}
    try:
        filepath, title = download_and_convert(url, user.id)
        sound = Sound.objects.create(
            owner=user,
            name=title,
            file=filepath,
            is_private=True,
        )
        return {
            "status": "ok",
            "sound_id": sound.id,
            "name": sound.name,
        }
    except Exception as error:
        return {
            "status": "failed",
            "detail": f"{error}",
        }


@shared_task
def upload_sound(user_id: int, temp_file, filename):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return {"error": "User not found."}

    basename, _ = os.path.splitext(filename)
    output_file = os.path.join("media", f"{basename}.ogg")

    command = [
        "ffmpeg",
        "-i",
        temp_file,
        "-c:a",
        "libopus",
        "-ar",
        "48000",
        "-ac",
        "1",
        "-b:a",
        "48k",
        output_file,
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)

        sound = Sound.objects.create(
            owner=user,
            name=basename,
            file=output_file,
            is_private=True,
        )
        return {
            "status": "ok",
            "sound_id": sound.id,
            "name": sound.name,
        }

    except subprocess.CalledProcessError as error:
        return {
            "status": "failed",
            "detail": f"{error.stderr}",
        }

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            logging.info("Cleaned up temp file.")
