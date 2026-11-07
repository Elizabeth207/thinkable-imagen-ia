"""Acceso a datos de archivos_multimedia."""

from uuid import UUID

from sqlalchemy import func, select

from app.extensions import db
from app.media.models import ArchivoMultimedia


def save_archivo(row: ArchivoMultimedia) -> ArchivoMultimedia:
    """Persiste un archivo multimedia y obtiene su id."""
    db.session.add(row)
    db.session.flush()
    return row


def find_owned(archivo_id: UUID, owner_id: UUID) -> ArchivoMultimedia | None:
    """Busca un archivo del propietario; None si no existe o no es suyo."""
    stmt = select(ArchivoMultimedia).where(
        ArchivoMultimedia.id == archivo_id,
        ArchivoMultimedia.propietario_id == owner_id,
    )
    return db.session.scalars(stmt).first()


def list_owned(owner_id: UUID, page: int, per_page: int) -> tuple[list, int]:
    """Lista paginada de archivos del propietario."""
    filters = ArchivoMultimedia.propietario_id == owner_id
    total = db.session.scalar(
        select(func.count()).select_from(ArchivoMultimedia).where(filters)
    ) or 0
    stmt = (
        select(ArchivoMultimedia)
        .where(filters)
        .order_by(ArchivoMultimedia.creado_en.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(db.session.scalars(stmt).all()), int(total)
