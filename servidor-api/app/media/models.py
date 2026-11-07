"""Modelo de la tabla archivos_multimedia."""

from uuid import UUID

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.common.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin
from app.extensions import db


class ArchivoMultimedia(UUIDPrimaryKeyMixin, CreatedAtMixin, db.Model):
    """Archivo de imagen original o resultado."""

    __tablename__ = "archivos_multimedia"
    __table_args__ = (
        CheckConstraint("tipo IN ('original', 'resultado')", name="tipo"),
        CheckConstraint("almacenamiento IN ('local', 'dropbox')", name="almacenamiento"),
        CheckConstraint("tamano_bytes > 0", name="tamano_bytes"),
    )

    propietario_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    espacio_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("espacios_trabajo.id", ondelete="RESTRICT"),
        nullable=False,
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    almacenamiento: Mapped[str] = mapped_column(String(20), nullable=False)
    referencia_externa: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ruta_logica: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tamano_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ancho: Mapped[int | None] = mapped_column(Integer, nullable=True)
    alto: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    nombre_original: Mapped[str | None] = mapped_column(String(255), nullable=True)
