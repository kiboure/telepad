import time
from random import randint
from urllib.parse import urlparse
from django.core.files.base import ContentFile
from celery import shared_task
from app.models import Sound
from users.models import User


@shared_task
def mock_download(pk: int, url: str):
    # Mock load time
    time.sleep(3)

    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return {"error": "User not found."}

    mock_id = randint(10000, 99999)
    file = ContentFile(b"mockfiledata", name=f"{user.username}_{mock_id}_mock.mp3")

    sound = Sound.objects.create(
        owner=user,
        name=f"{user.username}'s {urlparse(url).netloc}_{mock_id}",
        file=file,
        is_private=True,
    )

    return {"sound_id": sound.id, "name": sound.name}


@shared_task
def download_sound(pk: int, url: str):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return {"error": "User not found."}

    # sound = Sound.objects.create(
    #     owner=user,
    #     name=f"{user.username}'s {urlparse(url).netloc}_{mock_id}",
    #     file=file,
    #     is_private=True,
    # )

    # return {"sound_id": sound.id, "name": sound.name}
