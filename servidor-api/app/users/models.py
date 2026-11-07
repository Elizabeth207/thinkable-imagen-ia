"""Modelo de la tabla usuarios."""

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.common.mixins import CreatedUpdatedMixin, UUIDPrimaryKeyMixin
from app.extensions import db


class Usuario(UserMixin, UUIDPrimaryKeyMixin, CreatedUpdatedMixin, db.Model):
    """Cuenta de acceso al sistema."""

    __tablename__ = "usuarios"

    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(180), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activo")
    rol_global: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="usuario",
    )

    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo')", name="estado"),
        CheckConstraint(
            "rol_global IN ('usuario', 'admin_general')",
            name="rol_global",
        ),
        Index("uq_usuarios_correo_lower", func.lower(correo), unique=True),
    )

    @property
    def is_active(self) -> bool:
        """Flask-Login: solo cuentas activas siguen autenticadas."""
        return self.estado == "activo"

    def get_id(self) -> str:
        """Identificador de sesión para Flask-Login."""
        return str(self.id)

