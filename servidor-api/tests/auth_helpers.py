"""Ayudas HTTP para las pruebas de autenticación."""

from app.extensions import db
from app.users.repository import find_by_email


def csrf_headers(client) -> dict[str, str]:
    """Obtiene un token CSRF fresco y arma el encabezado."""
    response = client.get("/api/auth/csrf")
    token = response.get_json()["csrf_token"]
    return {"X-CSRFToken": token}


def register(
    client,
    correo: str = "ana@example.com",
    password: str = "password12345",
    nombre: str = "Ana",
    **extra,
):
    """Registra un usuario con CSRF cuando esté activo."""
    payload = {"nombre": nombre, "correo": correo, "contraseña": password, **extra}
    return client.post(
        "/api/auth/register",
        json=payload,
        headers=csrf_headers(client),
    )


def login(client, correo: str = "ana@example.com", password: str = "password12345"):
    """Inicia sesión enviando token CSRF."""
    return client.post(
        "/api/auth/login",
        json={"correo": correo, "contraseña": password},
        headers=csrf_headers(client),
    )


def deactivate_user(app, correo: str) -> None:
    """Marca la cuenta como inactiva en la base de pruebas."""
    with app.app_context():
        user = find_by_email(correo)
        user.estado = "inactivo"
        db.session.commit()
        db.session.expire_all()
