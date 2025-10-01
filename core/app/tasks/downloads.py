# -- IMPORTS --
import os
from celery import shared_task

from app.models import Sound
from app.utils import ydl_download, convert, upload_to_telegram, ffprobe_get_duration
from telepad.settings import MEDIA_ROOT


# -- TASKS --
@shared_task
def download_sound(user_id: int, url: str):
    path = None
    try:
        temp_file, info = ydl_download(url, user_id)
        title = info.get("title")
        duration = info.get("duration")

        name = os.path.splitext(os.path.basename(temp_file))[0]
        output_file = os.path.join(MEDIA_ROOT, f"{name}.ogg")
        convert(temp_file, output_file)

        file_id = upload_to_telegram("/media/" + path, title, duration)

        sound = Sound.objects.create(
            owner_id=user_id,
            name=title,
            file_id=file_id,
            duration=duration,
            is_private=True,
        )
        sound.saves.add(user_id)

        return {
            "status": "Ok",
            "sound_id": sound.id,
            "name": sound.name,
        }
    except Exception as error:
        return {
            "status": "Failed",
            "detail": str(error),
        }


@shared_task
def upload_sound(user_id: int, temp_file: str, filename: str):
    basename, _ = os.path.splitext(filename)
    output_file = os.path.join(MEDIA_ROOT, f"{basename}.ogg")

    duration = ffprobe_get_duration(temp_file)

    try:
        convert(temp_file, output_file)

        file_id = upload_to_telegram("/media/" + output_file, basename, duration)

        sound = Sound.objects.create(
            owner_id=user_id,
            name=basename,
            file=file_id,
            duration=duration,
            is_private=True,
        )
        sound.saves.add(user_id)

        return {
            "status": "Ok",
            "sound_id": sound.id,
            "name": sound.name,
        }

    except Exception as error:
        return {
            "status": "Failed",
            "detail": str(error),
        }
