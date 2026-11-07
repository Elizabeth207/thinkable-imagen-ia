"""Modelos de espacios_trabajo y membresias_espacio."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.common.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin, utc_now
from app.extensions import db


class EspacioTrabajo(UUIDPrimaryKeyMixin, CreatedAtMixin, db.Model):
    """Espacio individual o grupal de un usuario."""

    __tablename__ = "espacios_trabajo"

    propietario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activo")

    __table_args__ = (
        CheckConstraint("tipo IN ('individual', 'grupal')", name="tipo"),
        CheckConstraint("estado IN ('activo', 'inactivo')", name="estado"),
        UniqueConstraint("id", "tipo", name="uq_espacios_trabajo_id_tipo"),
        Index(
            "uq_espacios_propietario_individual",
            "propietario_id",
            unique=True,
            postgresql_where=text("tipo = 'individual'"),
        ),
    )


class MembresiaEspacio(UUIDPrimaryKeyMixin, db.Model):
    """Pertenencia de un usuario a un espacio."""

    __tablename__ = "membresias_espacio"

    usuario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    espacio_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    tipo_espacio: Mapped[str] = mapped_column(String(20), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False)
    unido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    __table_args__ = (
        CheckConstraint("tipo_espacio IN ('individual', 'grupal')", name="tipo_espacio"),
        CheckConstraint(
            "rol IN ('propietario', 'admin', 'participante')",
            name="rol",
        ),
        ForeignKeyConstraint(
            ["espacio_id", "tipo_espacio"],
            ["espacios_trabajo.id", "espacios_trabajo.tipo"],
            ondelete="CASCADE",
            name="fk_membresias_espacio_espacio_tipo",
        ),
        UniqueConstraint(
            "usuario_id",
            "espacio_id",
            name="uq_membresias_usuario_espacio",
        ),
        Index(
            "uq_membresias_usuario_grupal",
            "usuario_id",
            unique=True,
            postgresql_where=text("tipo_espacio = 'grupal'"),
        ),
    )
