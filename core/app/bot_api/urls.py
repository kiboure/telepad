from django.urls import path

from .views import BotListView

urlpatterns = [
    path("sounds/", BotListView.as_view(), name="bot-sounds"),
]