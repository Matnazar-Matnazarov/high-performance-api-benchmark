"""User routes: list (search, pagination), get by id, me (JWT), create (staff)."""

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from django_bolt import (
    IsAuthenticated,
    IsStaff,
    JWTAuthentication,
    PageNumberPagination,
)
from django_bolt.auth import AllowAny
from django_bolt.exceptions import HTTPException
from django_bolt.pagination import paginate
from accounts.schemas import UserCreateSchema, UserSchema

User = get_user_model()


def _query_params(request) -> dict:
    """Get query params from Bolt dict or Django HttpRequest."""
    if hasattr(request, "get") and callable(request.get):
        return request.get("query", {}) or {}
    q = getattr(request, "GET", None) or getattr(request, "query_params", None)
    return dict(q) if q else {}


def register(api):
    """Register user routes on the given BoltAPI."""

    @api.get("/users", auth=[], guards=[AllowAny()])
    @paginate(PageNumberPagination)
    async def list_users(request: HttpRequest):
        """List users with optional search. Paginated. Public."""
        qs = User.objects.only("id", "username").order_by("id")
        query = _query_params(request)
        search = (query.get("search") or "").strip()
        if search:
            qs = qs.filter(username__icontains=search)
        return qs

    @api.get("/users/{user_id}", auth=[], guards=[AllowAny()])
    async def get_user(request: HttpRequest, user_id: int) -> UserSchema:
        """Get user by ID. Public."""
        user = await User.objects.only("id", "username").filter(id=user_id).afirst()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserSchema.from_user(user)

    @api.get("/users/me", auth=[JWTAuthentication()], guards=[IsAuthenticated()])
    async def get_me(request: HttpRequest) -> UserSchema:
        """Current user. Requires JWT."""
        user = (
            await User.objects.only("id", "username")
            .filter(id=request.user.id)
            .afirst()
        )
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserSchema.from_user(user)

    @api.post(
        "/users",
        auth=[JWTAuthentication()],
        guards=[IsAuthenticated(), IsStaff()],
    )
    async def create_user(request: HttpRequest, body: UserCreateSchema) -> UserSchema:
        """Create user. Staff only."""
        if await User.objects.filter(username=body.username).aexists():
            raise HTTPException(status_code=400, detail="Username already exists")
        user = await sync_to_async(User.objects.create_user)(
            username=body.username,
            password=body.password,
            email=body.email or "",
        )
        return UserSchema.from_user(user)
