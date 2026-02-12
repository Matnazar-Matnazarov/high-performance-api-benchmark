"""DRF authentication: Bolt JWT (access_token from /auth/login/)."""

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication

User = get_user_model()


class BoltJWTAuthentication(authentication.BaseAuthentication):
    """Authenticate using Bolt-style JWT (Bearer token from create_jwt_for_user)."""

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization") or ""
        if not auth_header.startswith(f"{self.keyword} "):
            return None
        token = auth_header[len(self.keyword) + 1 :].strip()
        if not token:
            return None
        try:
            secret = getattr(settings, "BOLT_JWT_SECRET", None) or settings.SECRET_KEY
            algorithm = getattr(settings, "BOLT_JWT_ALGORITHM", "HS256")
            payload = jwt.decode(token, secret, algorithms=[algorithm])
        except jwt.InvalidTokenError:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        try:
            user = User.objects.get(pk=int(user_id))
        except (User.DoesNotExist, ValueError, TypeError):
            return None
        return (user, token)
