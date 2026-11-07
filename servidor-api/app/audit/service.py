"""Registro de eventos en la tabla auditoria."""

from uuid import UUID

from app.audit.models import Auditoria
from app.extensions import db


def record_event(
    accion: str,
    tipo_objetivo: str,
    usuario_id: UUID | None = None,
    objetivo_id: UUID | None = None,
) -> Auditoria:
    """Guarda un evento de auditoría sin datos sensibles."""
    row = Auditoria(
        usuario_id=usuario_id,
        accion=accion,
        tipo_objetivo=tipo_objetivo,
        objetivo_id=objetivo_id,
    )
    db.session.add(row)
    db.session.flush()
    return row
