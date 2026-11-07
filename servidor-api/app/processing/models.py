"""Modelos de proveedores_ia y procesamientos_ia."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.common.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin, utc_now
from app.extensions import db


class ProveedorIA(UUIDPrimaryKeyMixin, CreatedAtMixin, db.Model):
    """Proveedor externo de mejora de imágenes."""

    __tablename__ = "proveedores_ia"
    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo')", name="estado"),
    )

    nombre: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activo")


class ProcesamientoIA(UUIDPrimaryKeyMixin, db.Model):
    """Trabajo de mejora solicitado a un proveedor."""

    __tablename__ = "procesamientos_ia"

    usuario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    espacio_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("espacios_trabajo.id", ondelete="RESTRICT"),
        nullable=False,
    )
    proveedor_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("proveedores_ia.id", ondelete="RESTRICT"),
        nullable=True,
    )
    archivo_original_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("archivos_multimedia.id", ondelete="RESTRICT"),
        nullable=False,
    )
    archivo_resultado_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("archivos_multimedia.id", ondelete="RESTRICT"),
        nullable=True,
    )
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="pendiente")
    modelo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    version_modelo: Mapped[str | None] = mapped_column(String(80), nullable=True)
    parametros: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    proveedor_job_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    solicitado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    finalizado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    mensaje_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'en_proceso', 'completado', 'fallido')",
            name="estado",
        ),
        CheckConstraint(
            "estado <> 'completado' OR archivo_resultado_id IS NOT NULL",
            name="completado_con_resultado",
        ),
        UniqueConstraint(
            "proveedor_id",
            "proveedor_job_id",
            name="uq_procesamientos_proveedor_job",
        ),
        Index("ix_procesamientos_usuario_solicitado", "usuario_id", "solicitado_en"),
        Index("ix_procesamientos_espacio_estado", "espacio_id", "estado"),
    )
