"""CSRF en register, login, logout, change-password y ciclo de tokens."""

import pytest

from tests.auth_helpers import csrf_headers, login, register


@pytest.fixture()
def csrf_on(app):
    """Activa CSRF solo durante la prueba."""
    app.config["WTF_CSRF_ENABLED"] = True
    yield
    app.config["WTF_CSRF_ENABLED"] = False


def test_register_requires_csrf(auth_client, app, csrf_on):
    """Register sin token → csrf_failed; con token → 201."""
    bare = auth_client.post(
        "/api/auth/register",
        json={"nombre": "Ana", "correo": "ana@example.com", "contraseña": "password12345"},
    )
    assert bare.status_code == 400
    assert bare.get_json()["error"]["code"] == "csrf_failed"
    assert register(auth_client).status_code == 201


def test_login_requires_csrf(auth_client, app, csrf_on):
    """Login sin token → csrf_failed; con token → 200."""
    register(auth_client)
    auth_client.post("/api/auth/logout", headers=csrf_headers(auth_client))
    bare = auth_client.post(
        "/api/auth/login",
        json={"correo": "ana@example.com", "contraseña": "password12345"},
    )
    assert bare.status_code == 400
    assert bare.get_json()["error"]["code"] == "csrf_failed"
    assert login(auth_client).status_code == 200


def test_logout_requires_csrf(auth_client, app, csrf_on):
    """Logout sin token → csrf_failed; con token → 200."""
    register(auth_client)
    bare = auth_client.post("/api/auth/logout")
    assert bare.status_code == 400
    assert bare.get_json()["error"]["code"] == "csrf_failed"
    ok = auth_client.post("/api/auth/logout", headers=csrf_headers(auth_client))
    assert ok.status_code == 200


def test_change_password_requires_csrf(auth_client, app, csrf_on):
    """change-password sin token → csrf_failed; con token → 200."""
    register(auth_client)
    bare = auth_client.post(
        "/api/auth/change-password",
        json={"contraseña_actual": "password12345", "contraseña_nueva": "nueva1234567"},
    )
    assert bare.status_code == 400
    assert bare.get_json()["error"]["code"] == "csrf_failed"
    ok = auth_client.post(
        "/api/auth/change-password",
        json={"contraseña_actual": "password12345", "contraseña_nueva": "nueva1234567"},
        headers=csrf_headers(auth_client),
    )
    assert ok.status_code == 200


def test_csrf_token_cycle_after_login_logout(auth_client, app, csrf_on):
    """Tras login/logout el token anterior no vale; el nuevo sí."""
    register(auth_client)
    auth_client.post("/api/auth/logout", headers=csrf_headers(auth_client))
    t1 = auth_client.get("/api/auth/csrf").get_json()["csrf_token"]
    assert login(auth_client).status_code == 200
    stale = auth_client.post("/api/auth/logout", headers={"X-CSRFToken": t1})
    assert stale.status_code == 400
    t2 = auth_client.get("/api/auth/csrf").get_json()["csrf_token"]
    assert auth_client.post("/api/auth/logout", headers={"X-CSRFToken": t2}).status_code == 200
    t3 = auth_client.get("/api/auth/csrf").get_json()["csrf_token"]
    assert t3 != t2
    assert login(auth_client).status_code == 200
