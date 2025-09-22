from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views
from .botviews import BotListView

router = DefaultRouter()
router.register(r"", views.SoundViewSet, basename="sound")

urlpatterns = [
    path("download/", views.download, name="download"),
    path("upload/", views.upload, name="upload"),
    path("bot/", BotListView.as_view(), name="bot-list"),
]

urlpatterns += router.urls 