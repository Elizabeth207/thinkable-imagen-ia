"""Constructores mínimos de filas válidas para las pruebas."""

from app.audit.models import Auditoria
from app.extensions import db
from app.media.models import ArchivoMultimedia
from app.processing.models import ProcesamientoIA, ProveedorIA
from app.users.models import Usuario
from app.workspaces.models import EspacioTrabajo, MembresiaEspacio


def _add(row):
    """Añade la fila y obtiene su id sin hacer commit."""
    db.session.add(row)
    db.session.flush()
    return row


def make_usuario(**overrides) -> Usuario:
    """Crea un usuario válido en sesión."""
    data = {
        "nombre": "Ana",
        "correo": "ana@example.com",
        "password_hash": "hash",
        "estado": "activo",
        "rol_global": "usuario",
    }
    data.update(overrides)
    return _add(Usuario(**data))


def make_espacio(propietario_id, **overrides) -> EspacioTrabajo:
    """Crea un espacio válido en sesión."""
    data = {
        "propietario_id": propietario_id,
        "nombre": "Personal",
        "tipo": "individual",
        "estado": "activo",
    }
    data.update(overrides)
    return _add(EspacioTrabajo(**data))


def make_membresia(usuario_id, espacio_id, tipo_espacio, **overrides) -> MembresiaEspacio:
    """Crea una membresía válida en sesión."""
    data = {
        "usuario_id": usuario_id,
        "espacio_id": espacio_id,
        "tipo_espacio": tipo_espacio,
        "rol": "propietario",
    }
    data.update(overrides)
    return _add(MembresiaEspacio(**data))


def make_archivo(propietario_id, espacio_id, **overrides) -> ArchivoMultimedia:
    """Crea un archivo multimedia válido en sesión."""
    data = {
        "propietario_id": propietario_id,
        "espacio_id": espacio_id,
        "tipo": "original",
        "almacenamiento": "local",
        "ruta_logica": "users/a/original.png",
        "mime_type": "image/png",
        "tamano_bytes": 1024,
        "checksum_sha256": "a" * 64,
    }
    data.update(overrides)
    return _add(ArchivoMultimedia(**data))


def make_proveedor(**overrides) -> ProveedorIA:
    """Crea un proveedor de IA válido en sesión."""
    data = {"nombre": "replicate", "estado": "activo"}
    data.update(overrides)
    return _add(ProveedorIA(**data))


def make_procesamiento(usuario_id, espacio_id, archivo_id, **overrides) -> ProcesamientoIA:
    """Crea un procesamiento válido en sesión."""
    data = {
        "usuario_id": usuario_id,
        "espacio_id": espacio_id,
        "archivo_original_id": archivo_id,
        "estado": "pendiente",
    }
    data.update(overrides)
    return _add(ProcesamientoIA(**data))


def make_auditoria(**overrides) -> Auditoria:
    """Crea un registro de auditoría válido en sesión."""
    data = {"accion": "login", "tipo_objetivo": "usuario"}
    data.update(overrides)
    return _add(Auditoria(**data))
