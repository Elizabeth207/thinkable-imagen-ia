"""Roles, cambio de contraseña y límite de intentos."""

from app.extensions import db, limiter
from app.users.repository import find_by_email
from tests.auth_helpers import csrf_headers, login, register


def test_role_required_admin_route(auth_client, app):
    """Usuario normal 403; admin_general 200 en ruta temporal de prueba."""
    register(auth_client)
    login(auth_client)
    assert auth_client.get("/api/_test/admin-only").status_code == 403
    with app.app_context():
        user = find_by_email("ana@example.com")
        user.rol_global = "admin_general"
        db.session.commit()
    assert auth_client.get("/api/_test/admin-only").status_code == 200


def test_change_password_flow(auth_client, app):
    """Cambio correcto invalida la antigua; actual incorrecta falla."""
    register(auth_client)
    assert login(auth_client).status_code == 200
    bad = auth_client.post(
        "/api/auth/change-password",
        json={"contraseña_actual": "no-es-esta12", "contraseña_nueva": "nueva1234567"},
        headers=csrf_headers(auth_client),
    )
    assert bad.status_code == 400
    ok = auth_client.post(
        "/api/auth/change-password",
        json={
            "contraseña_actual": "password12345",
            "contraseña_nueva": "nueva1234567",
        },
        headers=csrf_headers(auth_client),
    )
    assert ok.status_code == 200
    auth_client.post("/api/auth/logout", headers=csrf_headers(auth_client))
    assert login(auth_client, password="password12345").status_code == 401
    assert login(auth_client, password="nueva1234567").status_code == 200


def test_change_password_rejects_reuse(auth_client, app):
    """Nueva igual a la actual → 400 same_password."""
    register(auth_client)
    assert login(auth_client).status_code == 200
    response = auth_client.post(
        "/api/auth/change-password",
        json={
            "contraseña_actual": "password12345",
            "contraseña_nueva": "password12345",
        },
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "same_password"


def test_login_rate_limit(auth_client, app):
    """Tras el máximo de intentos, login responde 429."""
    with app.app_context():
        limiter.reset()
    app.config["LOGIN_RATE_LIMIT"] = "3 per minute"
    register(auth_client)
    for _ in range(3):
        login(auth_client, password="password_wrong1")
    blocked = login(auth_client, password="password_wrong1")
    assert blocked.status_code == 429
    assert blocked.get_json()["error"]["code"] == "rate_limited"
    with app.app_context():
        limiter.reset()
    app.config["LOGIN_RATE_LIMIT"] = "1000 per minute"
