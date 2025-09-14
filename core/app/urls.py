from rest_framework.routers import DefaultRouter
from .views import SoundViewSet

router = DefaultRouter()
router.register(r"sounds", SoundViewSet, basename="sound")

urlpatterns = router.urls