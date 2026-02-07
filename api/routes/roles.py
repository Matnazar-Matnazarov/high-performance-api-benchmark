"""Role routes: list roles (from User.Role TextChoices)."""

from django.http import HttpRequest

from django_bolt.auth import AllowAny
from django_bolt.exceptions import HTTPException
from accounts.models import Role
from accounts.schemas import RoleSchema


def register(api):
    """Register role routes on the given BoltAPI."""

    @api.get("/roles", auth=[], guards=[AllowAny()])
    async def list_roles(request: HttpRequest) -> list[RoleSchema]:
        """List all roles (ADMIN, SHOPKEEPER, CUSTOMER). Public."""
        return [RoleSchema(code=choice.value, name=choice.label) for choice in Role]

    @api.get("/roles/code/{code}", auth=[], guards=[AllowAny()])
    async def get_role_by_code(request: HttpRequest, code: str) -> RoleSchema:
        """Get role by code (ADMIN, SHOPKEEPER, CUSTOMER). Public."""
        code = (code or "").strip().upper()
        for choice in Role:
            if choice.value == code:
                return RoleSchema(code=choice.value, name=choice.label)
        raise HTTPException(status_code=404, detail="Role not found")
