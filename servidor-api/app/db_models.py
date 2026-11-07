"""Importa todos los modelos para que Alembic los detecte."""

from app.audit.models import Auditoria
from app.media.models import ArchivoMultimedia
from app.processing.models import ProcesamientoIA, ProveedorIA
from app.users.models import Usuario
from app.workspaces.models import EspacioTrabajo, MembresiaEspacio

__all__ = [
    "ArchivoMultimedia",
    "Auditoria",
    "EspacioTrabajo",
    "MembresiaEspacio",
    "ProcesamientoIA",
    "ProveedorIA",
    "Usuario",
]
