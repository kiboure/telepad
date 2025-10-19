from django.urls import include, path
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    # Mounted at root; Nginx strips /api/ prefix before proxying
    path("", include(("users.urls", "users"), namespace="users")),
    path("", include(("app.urls", "app"), namespace="app")),
    path("bot/", include(("app.bot_api.urls", "app"), namespace="bot_api")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
