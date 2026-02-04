"""Auth routes: POST /auth/login (JWT)."""

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpRequest

from django_bolt import create_jwt_for_user
from django_bolt.exceptions import HTTPException

from accounts.schemas import LoginSchema, TokenSchema


def register(api):
    """Register auth routes on the given BoltAPI."""

    @api.post("/auth/login")
    async def login(request: HttpRequest, body: LoginSchema) -> TokenSchema:
        """Obtain JWT access token. No auth required."""
        user = await sync_to_async(authenticate)(
            username=body.username,
            password=body.password,
        )
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        secret = getattr(settings, "BOLT_JWT_SECRET", None) or settings.SECRET_KEY
        expires_in = getattr(settings, "BOLT_JWT_EXPIRES_SECONDS", 3600)
        access_token = create_jwt_for_user(
            user,
            secret=secret,
            algorithm=getattr(settings, "BOLT_JWT_ALGORITHM", "HS256"),
            expires_in=expires_in,
        )
        return TokenSchema(
            access_token=access_token,
            expires_in=expires_in,
            token_type="bearer",
        )
