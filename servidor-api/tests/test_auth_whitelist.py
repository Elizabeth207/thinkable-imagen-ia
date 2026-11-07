"""Lista blanca de campos en login y change-password."""

from tests.auth_helpers import csrf_headers, login, register


def test_login_rejects_extra_fields(auth_client, app):
    """Login con campos extra → 400 validation_error."""
    register(auth_client)
    response = auth_client.post(
        "/api/auth/login",
        json={
            "correo": "ana@example.com",
            "contraseña": "password12345",
            "rol_global": "admin_general",
        },
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 400
    err = response.get_json()["error"]
    assert err["code"] == "validation_error"
    assert err["fields"]["rol_global"] == "Campo no permitido."


def test_change_password_rejects_extra_fields(auth_client, app):
    """change-password con campos extra → 400 validation_error."""
    register(auth_client)
    login(auth_client)
    response = auth_client.post(
        "/api/auth/change-password",
        json={
            "contraseña_actual": "password12345",
            "contraseña_nueva": "nueva1234567",
            "estado": "activo",
        },
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 400
    err = response.get_json()["error"]
    assert err["code"] == "validation_error"
    assert err["fields"]["estado"] == "Campo no permitido."
