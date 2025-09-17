from celery import shared_task
from app.models import Sound
from users.models import User
from app.downloader import download_and_convert


@shared_task
def download_sound(pk: int, url: str):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return {"error": "User not found."}

    try:
        filepath, title = download_and_convert(url, user.id)
        sound = Sound.objects.create(
            owner=user,
            name=title,
            file=filepath,
            is_private=True,
        )
        output = {"status": "ok", "sound_id": sound.id, "name": sound.name}
    except Exception as error:
        output = {"status": "failed", "detail": f"{error}"}

    return output
