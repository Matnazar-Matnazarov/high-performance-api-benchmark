"""DRF async views: health, auth, roles, users (Bolt-compatible endpoints)."""

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import connection
from rest_framework import serializers as rf_serializers

from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from drf_spectacular.types import OpenApiTypes
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


@extend_schema(
    tags=["Health"],
    summary="Liveness probe",
    description="Returns service liveness status. Used by orchestrators (e.g. Kubernetes) to verify the process is running.",
    responses={
        200: {
            "type": "object",
            "properties": {"status": {"type": "string", "example": "ok"}},
        }
    },
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
async def health_view(request):
    """GET /health - liveness."""
    return Response({"status": "ok"})


@extend_schema(
    tags=["Health"],
    summary="Custom health check",
    description="Extended health check endpoint returning status and a custom message.",
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "ok"},
                "message": {"type": "string", "example": "Test health check endpoint"},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
async def health_test_view(request):
    """GET /health/test - custom health check."""
    return Response({"status": "ok", "message": "Test health check endpoint"})


@extend_schema(
    tags=["Health"],
    summary="Readiness probe",
    description="Returns service readiness status. Verifies database connectivity. Returns 503 if DB is unreachable.",
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "healthy"},
                "checks": {
                    "type": "object",
                    "properties": {"database": {"type": "string", "example": "ok"}},
                },
            },
        },
        503: {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "unhealthy"},
                "checks": {
                    "type": "object",
                    "properties": {"database": {"type": "string", "example": "error"}},
                },
            },
        },
    },
)
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


@extend_schema(
    tags=["Roles"],
    summary="List all roles",
    description="Returns the list of available user roles (ADMIN, SHOPKEEPER, CUSTOMER).",
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"code": {"type": "string"}, "name": {"type": "string"}},
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
async def role_list_view(request):
    """GET /roles - list roles."""
    return Response([{"code": c, "name": n} for c, n in Role.choices])


@extend_schema(
    tags=["Roles"],
    summary="Get role by code",
    description="Returns a single role by its code (e.g. ADMIN, SHOPKEEPER, CUSTOMER).",
    parameters=[
        OpenApiParameter(
            "code", OpenApiTypes.STR, OpenApiParameter.PATH, description="Role code"
        )
    ],
    responses={
        200: {
            "type": "object",
            "properties": {"code": {"type": "string"}, "name": {"type": "string"}},
        },
        404: {
            "type": "object",
            "properties": {"detail": {"type": "string", "example": "Role not found"}},
        },
    },
)
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


LoginRequestSerializer = inline_serializer(
    name="LoginRequest",
    fields={
        "username": rf_serializers.CharField(help_text="Username"),
        "password": rf_serializers.CharField(
            help_text="Password", style={"input_type": "password"}
        ),
    },
)

LoginResponseSerializer = inline_serializer(
    name="LoginResponse",
    fields={
        "access_token": rf_serializers.CharField(help_text="JWT access token"),
        "expires_in": rf_serializers.IntegerField(help_text="Token expiry in seconds"),
        "token_type": rf_serializers.CharField(help_text="Bearer"),
    },
)


@extend_schema(
    tags=["Auth"],
    summary="Login (Bolt-style JWT)",
    description="Authenticate with username and password. Returns Bolt-compatible JWT (access_token, expires_in, token_type). Use the token in Authorization: Bearer <access_token>.",
    request=LoginRequestSerializer,
    responses={
        200: LoginResponseSerializer,
        401: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "example": "Invalid credentials"}
            },
        },
    },
)
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

    serializer_class = UserSerializer
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

    @extend_schema(
        tags=["Users"],
        summary="List users",
        description="Paginated list of users. Supports ?search= and ?role= / ?role_code= filters.",
        parameters=[
            OpenApiParameter(
                "page",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Page number",
            ),
            OpenApiParameter(
                "page_size",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Items per page",
            ),
            OpenApiParameter(
                "search",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by username",
            ),
            OpenApiParameter(
                "role",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by role (ADMIN, SHOPKEEPER, CUSTOMER)",
            ),
        ],
        responses={200: UserSerializer(many=True)},
    )
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

    @extend_schema(
        tags=["Users"],
        summary="Get user by ID",
        description="Returns a single user by primary key.",
        responses={
            200: UserSerializer,
            404: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "User not found"}
                },
            },
        },
    )
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

    @extend_schema(
        tags=["Users"],
        summary="Create user",
        description="Create a new user. Requires staff/admin authentication.",
        request=UserCreateSerializer,
        responses={201: UserSerializer},
    )
    async def acreate(self, request):
        """POST /users - create user (staff only)."""
        serializer = UserCreateSerializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        user = await sync_to_async(serializer.save)()
        out = UserSerializer(user)
        data = await sync_to_async(lambda: out.data)()
        return Response(data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["Users"],
        summary="Current user",
        description="Returns the authenticated user's profile. Requires JWT.",
        responses={200: UserSerializer},
    )
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
