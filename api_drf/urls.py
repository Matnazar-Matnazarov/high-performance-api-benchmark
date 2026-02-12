"""DRF API URL configuration."""

from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

router = SimpleRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("health/", views.health_view),
    path("health/test/", views.health_test_view),
    path("ready/", views.ready_view),
    path("roles/", views.role_list_view),
    path("roles/code/<str:code>/", views.role_detail_view),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("", include(router.urls)),
]
