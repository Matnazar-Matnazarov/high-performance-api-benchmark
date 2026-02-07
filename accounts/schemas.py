import msgspec
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import Role

User = get_user_model()


# ----- Auth -----
class LoginSchema(msgspec.Struct):
    """Request body for POST /auth/login."""

    username: str
    password: str


class TokenSchema(msgspec.Struct):
    """JWT token response."""

    access_token: str
    expires_in: int
    token_type: str = "bearer"


# ----- Roles (from Role TextChoices) -----
class RoleSchema(msgspec.Struct):
    """Role option for API (code + display name)."""

    code: str
    name: str


# ----- Users -----
class UserSchema(msgspec.Struct):
    """User response (id, username, role)."""

    id: int
    username: str
    role: str

    @classmethod
    def from_user(cls, user: User) -> "UserSchema":
        return cls(
            id=user.id,
            username=user.username,
            role=user.role or Role.CUSTOMER,
        )


class UserCreateSchema(msgspec.Struct):
    """Request body for POST /users (create user)."""

    username: str
    password: str
    email: str = ""
    role: str = Role.CUSTOMER


# User schema for Django Admin
class UserAdminSchema(msgspec.Struct):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_staff: bool
    is_superuser: bool
    last_login: timezone.datetime

    @classmethod
    def from_user(cls, user: User) -> "UserAdminSchema":
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            last_login=user.last_login or timezone.now(),
        )
