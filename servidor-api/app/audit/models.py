"""Modelo de la tabla auditoria."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.common.mixins import UUIDPrimaryKeyMixin, utc_now
from app.extensions import db


class Auditoria(UUIDPrimaryKeyMixin, db.Model):
    """Registro de una acción relevante del sistema."""

    __tablename__ = "auditoria"
    __table_args__ = (Index("ix_auditoria_fecha", "fecha"),)

    usuario_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )
    accion: Mapped[str] = mapped_column(String(80), nullable=False)
    tipo_objetivo: Mapped[str] = mapped_column(String(60), nullable=False)
    objetivo_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
