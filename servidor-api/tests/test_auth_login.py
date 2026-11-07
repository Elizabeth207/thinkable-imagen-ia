"""Pruebas de login, logout y /me."""

from tests.auth_helpers import csrf_headers, deactivate_user, login, register


def test_login_and_me_hide_password_hash(auth_client, app):
    """Login correcto y /me no incluyen password_hash."""
    register(auth_client)
    assert login(auth_client).status_code == 200
    me = auth_client.get("/api/auth/me")
    assert me.status_code == 200
    user = me.get_json()["user"]
    assert user["correo"] == "ana@example.com"
    assert "password_hash" not in user


def test_login_invalid_same_message(auth_client, app):
    """Correo inexistente y contraseña incorrecta → mismo 401."""
    register(auth_client)
    missing = login(auth_client, correo="nadie@example.com")
    wrong = login(auth_client, password="password_wrong1")
    assert missing.status_code == wrong.status_code == 401
    assert missing.get_json() == wrong.get_json()
    assert missing.get_json()["error"]["message"] == "credenciales inválidas"


def test_inactive_account_403_and_session_dropped(auth_client, app):
    """Cuenta inactiva: 403 en login; sesión abierta queda invalidada."""
    register(auth_client)
    assert login(auth_client).status_code == 200
    deactivate_user(app, "ana@example.com")
    assert auth_client.get("/api/auth/me").status_code == 401
    again = login(auth_client)
    assert again.status_code == 403
    assert again.get_json()["error"]["code"] == "account_inactive"


def test_logout_invalidates_session(auth_client, app):
    """Logout deja /me en 401."""
    register(auth_client)
    login(auth_client)
    out = auth_client.post("/api/auth/logout", headers=csrf_headers(auth_client))
    assert out.status_code == 200
    assert auth_client.get("/api/auth/me").status_code == 401


def test_protected_without_session_401_json(auth_client, app):
    """Rutas protegidas sin sesión responden 401 JSON."""
    response = auth_client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "unauthorized"
