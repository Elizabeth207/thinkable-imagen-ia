"""Clave UUID y marcas de tiempo reutilizables."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


def utc_now() -> datetime:
    """Instantánea actual en UTC con zona horaria."""
    return datetime.now(timezone.utc)


class UUIDPrimaryKeyMixin:
    """Clave primaria UUID generada en la aplicación."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class CreatedAtMixin:
    """Fecha de creación con zona horaria."""

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )


class CreatedUpdatedMixin(CreatedAtMixin):
    """Fechas de creación y actualización con zona horaria."""

    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
