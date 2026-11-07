"""Formato JSON uniforme de errores (sin HTML)."""

from app.extensions import limiter
from tests.auth_helpers import deactivate_user, login, register


def _assert_json_error(response, status: int, code: str) -> None:
    assert response.status_code == status
    assert response.content_type.startswith("application/json")
    body = response.get_json()
    assert set(body["error"]) >= {"code", "message"}
    assert body["error"]["code"] == code
    assert "<html" not in response.get_data(as_text=True).lower()


def test_401_unauthorized_json(auth_client, app):
    """Sin sesión: 401 JSON."""
    _assert_json_error(auth_client.get("/api/auth/me"), 401, "unauthorized")


def test_403_forbidden_json(auth_client, app):
    """Usuario sin rol admin: 403 JSON."""
    register(auth_client)
    login(auth_client)
    _assert_json_error(auth_client.get("/api/_test/admin-only"), 403, "forbidden")


def test_404_not_found_json(auth_client, app):
    """Ruta inexistente: 404 JSON."""
    _assert_json_error(auth_client.get("/api/no-existe"), 404, "not_found")


def test_405_method_not_allowed_json(auth_client, app):
    """Método no permitido: 405 JSON."""
    response = auth_client.delete("/api/auth/me")
    assert response.status_code == 405
    assert response.content_type.startswith("application/json")
    assert response.get_json()["error"]["code"]
    assert "<html" not in response.get_data(as_text=True).lower()


def test_500_server_error_json(auth_client, app):
    """Error no controlado: 500 JSON."""
    _assert_json_error(auth_client.get("/api/_test/boom"), 500, "server_error")


def test_csrf_failed_json(auth_client, app):
    """CSRF inválido: 400 csrf_failed JSON."""
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        response = auth_client.post(
            "/api/auth/login",
            json={"correo": "a@b.co", "contraseña": "x"},
        )
        _assert_json_error(response, 400, "csrf_failed")
    finally:
        app.config["WTF_CSRF_ENABLED"] = False


def test_rate_limited_json_with_retry_after(auth_client, app):
    """Límite de intentos: 429 rate_limited JSON."""
    with app.app_context():
        limiter.reset()
    app.config["LOGIN_RATE_LIMIT"] = "2 per minute"
    register(auth_client)
    login(auth_client, password="password_wrong1")
    login(auth_client, password="password_wrong1")
    blocked = login(auth_client, password="password_wrong1")
    _assert_json_error(blocked, 429, "rate_limited")
    with app.app_context():
        limiter.reset()
    app.config["LOGIN_RATE_LIMIT"] = "1000 per minute"


def test_inactive_user_me_401(auth_client, app):
    """Cuenta desactivada en BD: /me con la misma cookie → 401."""
    register(auth_client)
    assert auth_client.get("/api/auth/me").status_code == 200
    deactivate_user(app, "ana@example.com")
    _assert_json_error(auth_client.get("/api/auth/me"), 401, "unauthorized")
