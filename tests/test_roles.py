"""Role endpoints and schema tests (sync, in-process)."""


def test_role_schema():
    """RoleSchema has code and name."""
    from accounts.schemas import RoleSchema

    s = RoleSchema(code="ADMIN", name="Administrator")
    assert s.code == "ADMIN"
    assert s.name == "Administrator"


def test_roles_list(client):
    """GET /roles returns list of roles (ADMIN, SHOPKEEPER, CUSTOMER)."""
    r = client.get("/roles")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    codes = [item["code"] for item in data]
    assert "ADMIN" in codes
    assert "SHOPKEEPER" in codes
    assert "CUSTOMER" in codes
    for item in data:
        assert "code" in item
        assert "name" in item


def test_roles_get_by_code(client):
    """GET /roles/code/ADMIN returns ADMIN role."""
    r = client.get("/roles/code/ADMIN")
    assert r.status_code == 200
    data = r.json()
    assert data["code"] == "ADMIN"
    assert data["name"] == "Administrator"


def test_roles_get_by_code_not_found(client):
    """GET /roles/code/INVALID returns 404."""
    r = client.get("/roles/code/INVALID")
    assert r.status_code == 404
