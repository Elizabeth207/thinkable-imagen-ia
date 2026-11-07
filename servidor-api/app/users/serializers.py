"""Serialización pública de usuarios. Nunca incluye password_hash."""

from app.users.models import Usuario


def serialize_user(user: Usuario) -> dict:
    """Devuelve los campos seguros del usuario autenticado."""
    return {
        "id": str(user.id),
        "nombre": user.nombre,
        "correo": user.correo,
        "estado": user.estado,
        "rol_global": user.rol_global,
        "creado_en": user.creado_en.isoformat(),
    }
