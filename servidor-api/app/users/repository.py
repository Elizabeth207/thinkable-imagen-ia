"""Acceso a datos de usuarios."""

from uuid import UUID

from sqlalchemy import func, select

from app.extensions import db
from app.users.models import Usuario


def find_by_email(correo: str) -> Usuario | None:
    """Busca un usuario por correo normalizado (sin importar mayúsculas)."""
    stmt = select(Usuario).where(func.lower(Usuario.correo) == correo.lower())
    return db.session.scalars(stmt).first()


def find_by_id(user_id: UUID | str) -> Usuario | None:
    """Busca un usuario por su identificador."""
    try:
        key = user_id if isinstance(user_id, UUID) else UUID(str(user_id))
    except ValueError:
        return None
    return db.session.get(Usuario, key)


def save(user: Usuario) -> Usuario:
    """Persiste un usuario nuevo o actualizado."""
    db.session.add(user)
    db.session.flush()
    return user
