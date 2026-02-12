"""DRF async views: health, auth, roles, users (Bolt-compatible endpoints)."""

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import connection
from rest_framework import permissions, status
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from adrf.decorators import api_view
from adrf.views import APIView as AsyncAPIView
from adrf.viewsets import ViewSet
from django_bolt import create_jwt_for_user

from accounts.models import Role
from django.contrib.auth import get_user_model

from .serializers import UserCreateSerializer, UserSerializer

User = get_user_model()
VALID_ROLES = {Role.ADMIN, Role.SHOPKEEPER, Role.CUSTOMER}


# ----- Health (async) -----


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
async def health_view(request):
    """GET /health - liveness."""
    return Response({"status": "ok"})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
async def health_test_view(request):
    """GET /health/test - custom health check."""
    return Response({"status": "ok", "message": "Test health check endpoint"})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
async def ready_view(request):
    """GET /ready - readiness (DB check)."""
    try:
        await sync_to_async(connection.ensure_connection)()
        return Response({"status": "healthy", "checks": {"database": "ok"}})
    except Exception:
        return Response(
            {"status": "unhealthy", "checks": {"database": "error"}},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# ----- Roles (async) -----


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
async def role_list_view(request):
    """GET /roles - list roles."""
    return Response([{"code": c, "name": n} for c, n in Role.choices])


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
async def role_detail_view(request, code):
    """GET /roles/code/{code}."""
    code_upper = code.upper()
    for c, n in Role.choices:
        if c == code_upper:
            return Response({"code": c, "name": n})
    return Response({"detail": "Role not found"}, status=status.HTTP_404_NOT_FOUND)


# ----- Auth: Bolt-compatible login (access_token format) -----


class BoltLoginView(AsyncAPIView):
    """POST /auth/login - Bolt-compatible JWT (access_token, expires_in, token_type)."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    async def post(self, request):
        username = request.data.get("username") or ""
        password = request.data.get("password") or ""
        user = await sync_to_async(authenticate)(
            username=username,
            password=password,
        )
        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        secret = getattr(settings, "BOLT_JWT_SECRET", None) or settings.SECRET_KEY
        expires_in = getattr(settings, "BOLT_JWT_EXPIRES_SECONDS", 3600)
        access_token = create_jwt_for_user(
            user,
            secret=secret,
            algorithm=getattr(settings, "BOLT_JWT_ALGORITHM", "HS256"),
            expires_in=expires_in,
        )
        return Response(
            {
                "access_token": access_token,
                "expires_in": expires_in,
                "token_type": "bearer",
            }
        )


# ----- Users (async ViewSet) -----


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class UserViewSet(ViewSet):
    """Async user endpoints: list, retrieve, create, me."""

    permission_classes = [permissions.AllowAny]
    pagination_class = UserPagination

    def get_queryset(self):
        return User.objects.only("id", "username", "role").order_by("id")

    def _filter_queryset(self, qs):
        search = (self.request.query_params.get("search") or "").strip()
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
        if self.action in ("create", "acreate"):
            return [permissions.IsAdminUser()]
        if self.action in ("me", "ame"):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    async def alist(self, request):
        """GET /users - paginated list with search and role filter."""
        qs = self.get_queryset()
        qs = await sync_to_async(self._filter_queryset)(qs)
        paginator = self.pagination_class()
        page = await sync_to_async(paginator.paginate_queryset)(qs, request, view=self)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            data = await sync_to_async(lambda: serializer.data)()
            return paginator.get_paginated_response(data)
        serializer = UserSerializer(qs, many=True)
        data = await sync_to_async(lambda: serializer.data)()
        return Response(data)

    async def aretrieve(self, request, pk=None):
        """GET /users/{id} - get user by ID."""
        user = await User.objects.filter(pk=pk).only("id", "username", "role").afirst()
        if user is None:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserSerializer(user)
        data = await sync_to_async(lambda: serializer.data)()
        return Response(data)

    async def acreate(self, request):
        """POST /users - create user (staff only)."""
        serializer = UserCreateSerializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        user = await sync_to_async(serializer.save)()
        out = UserSerializer(user)
        data = await sync_to_async(lambda: out.data)()
        return Response(data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="me",
    )
    async def ame(self, request):
        """GET /users/me - current user."""
        serializer = UserSerializer(request.user)
        data = await sync_to_async(lambda: serializer.data)()
        return Response(data)
