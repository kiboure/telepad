# -- IMPORTS --
import os
import traceback
from celery import shared_task

from app.models import Sound
from app.utils import ydl_download, convert, upload_to_telegram, ffprobe_get_duration
from core.settings import MEDIA_ROOT


# -- TASKS --
@shared_task
def download_sound(user_id: int, url: str):
    try:
        temp_file, info = ydl_download(url, user_id)
        title = info.get("title")
    
        name = f"{os.path.splitext(os.path.basename(temp_file))[0]}.ogg"
        output_file = os.path.join(MEDIA_ROOT, name)
        convert(temp_file, output_file)

        duration = ffprobe_get_duration(output_file)

        file_id = upload_to_telegram(output_file, title, duration)

        sound = Sound.objects.create(
            owner_id=user_id,
            name=title,
            file_path=name,
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
        traceback.print_exc()
        return {
            "status": "Failed",
            "detail": str(error),
        }


@shared_task
def upload_sound(user_id: int, temp_file: str, filename: str):
    basename, _ = os.path.splitext(os.path.basename(filename))
    output_file = os.path.join(MEDIA_ROOT, f"{basename}.ogg")

    try:
        convert(temp_file, output_file)
        duration = ffprobe_get_duration(output_file)
        file_id = upload_to_telegram(output_file, basename, duration)

        sound = Sound.objects.create(
            owner_id=user_id,
            name=basename,
            file_path=os.path.basename(output_file),
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
