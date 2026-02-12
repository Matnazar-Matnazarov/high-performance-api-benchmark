"""DRF views: health, auth, roles, users."""

from rest_framework import permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import Role
from django.contrib.auth import get_user_model

from .serializers import UserCreateSerializer, UserSerializer

User = get_user_model()
VALID_ROLES = {Role.ADMIN, Role.SHOPKEEPER, Role.CUSTOMER}


# ----- Health -----


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health_view(request):
    """GET /health - liveness."""
    return Response({"status": "ok"})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health_test_view(request):
    """GET /health/test - custom health check."""
    return Response({"status": "ok", "message": "Test health check endpoint"})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def ready_view(request):
    """GET /ready - readiness (DB check)."""
    from django.db import connection

    try:
        connection.ensure_connection()
        return Response({"status": "healthy", "checks": {"database": "ok"}})
    except Exception:
        return Response(
            {"status": "unhealthy", "checks": {"database": "error"}},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# ----- Roles -----


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def role_list_view(request):
    """GET /roles - list roles."""
    return Response([{"code": c, "name": n} for c, n in Role.choices])


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def role_detail_view(request, code):
    """GET /roles/code/{code}."""
    code_upper = code.upper()
    for c, n in Role.choices:
        if c == code_upper:
            return Response({"code": c, "name": n})
    return Response({"detail": "Role not found"}, status=status.HTTP_404_NOT_FOUND)


# ----- Users -----


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class UserViewSet(ModelViewSet):
    queryset = User.objects.only("id", "username", "role").order_by("id")
    serializer_class = UserSerializer
    pagination_class = UserPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(username__icontains=search)
        role = (
            (
                self.request.query_params.get("role")
                or self.request.query_params.get("role_code")
                or ""
            )
            .strip()
            .upper()
        )
        if role and role in VALID_ROLES:
            qs = qs.filter(role=role)
        return qs

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAdminUser()]
        if self.action == "me":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """GET /users/me - current user."""
        return Response(UserSerializer(request.user).data)
