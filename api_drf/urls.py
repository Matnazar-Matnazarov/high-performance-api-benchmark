"""DRF async API URL configuration (Bolt-compatible endpoints)."""

from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView

from adrf import routers

from . import views

router = routers.SimpleRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    path("health/", views.health_view),
    path("health/test/", views.health_test_view),
    path("ready/", views.ready_view),
    path("roles/", views.role_list_view),
    path("roles/code/<str:code>/", views.role_detail_view),
    # Bolt-compatible: access_token, expires_in, token_type
    path("auth/login/", views.BoltLoginView.as_view(), name="token_obtain_bolt"),
    # SimpleJWT: access, refresh (alternative)
    path("auth/login/jwt/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("", include(router.urls)),
]
