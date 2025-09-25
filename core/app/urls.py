from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views
from .botviews import BotListView

router = DefaultRouter()
router.register(r"sounds", views.SoundViewSet, basename="sound")

urlpatterns = [
    path("sounds/download/", views.download, name="download"),
    path("sounds/upload/", views.upload, name="upload"),
    path("bot/sounds/", BotListView.as_view(), name="bot-sounds"),
]

urlpatterns += router.urls 