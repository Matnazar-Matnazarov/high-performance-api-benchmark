"""Unit tests for schemas (no server required)."""

import pytest
from django.contrib.auth import get_user_model

from accounts.models import Role
from accounts.schemas import (
    LoginSchema,
    RoleSchema,
    TokenSchema,
    UserCreateSchema,
    UserSchema,
)

User = get_user_model()


@pytest.mark.django_db
def test_user_schema_from_user():
    """UserSchema.from_user builds schema from User with role."""
    user = User(id=1, username="testuser", role=Role.SHOPKEEPER)
    schema = UserSchema.from_user(user)
    assert schema.id == 1
    assert schema.username == "testuser"
    assert schema.role == Role.SHOPKEEPER


@pytest.mark.django_db
def test_user_schema_from_user_default_role():
    """UserSchema.from_user uses CUSTOMER when role is empty."""
    user = User(id=2, username="norole", role=None)
    schema = UserSchema.from_user(user)
    assert schema.role == Role.CUSTOMER


def test_login_schema():
    """LoginSchema accepts username and password."""
    s = LoginSchema(username="u", password="p")
    assert s.username == "u"
    assert s.password == "p"


def test_token_schema():
    """TokenSchema has access_token, token_type, expires_in."""
    s = TokenSchema(access_token="jwt.here", expires_in=3600)
    assert s.access_token == "jwt.here"
    assert s.token_type == "bearer"
    assert s.expires_in == 3600


def test_role_schema():
    """RoleSchema has code and name."""
    s = RoleSchema(code="ADMIN", name="Administrator")
    assert s.code == "ADMIN"
    assert s.name == "Administrator"


def test_user_create_schema():
    """UserCreateSchema accepts username, password, optional email and role."""
    s = UserCreateSchema(username="u", password="p", email="e@e.com")
    assert s.username == "u"
    assert s.password == "p"
    assert s.email == "e@e.com"
    assert s.role == Role.CUSTOMER

    s2 = UserCreateSchema(username="a", password="b", role=Role.ADMIN)
    assert s2.role == Role.ADMIN
