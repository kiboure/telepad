from django.urls import include, path
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path("api/", include(("users.urls", "users"), namespace="users")),
    path("api/sounds/", include(("app.urls", "app"), namespace="app")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)