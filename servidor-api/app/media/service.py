"""Orquesta validación, almacenamiento y registro de imágenes."""

import io
import uuid
from uuid import UUID

from flask import current_app
from flask_login import current_user
from motor_ia.errors import InvalidImageError
from sqlalchemy.exc import SQLAlchemyError

from app.audit.service import record_event
from app.extensions import db
from app.media.errors import MediaError
from app.media.models import ArchivoMultimedia
from app.media.repository import find_owned, list_owned, save_archivo
from app.media.validation import UploadTooLargeError, ValidatedUpload, validate_upload
from app.storage.factory import get_storage
from app.workspaces.repository import find_individual_workspace


def upload_image(file_storage, form_keys: set[str], file_keys: set[str]) -> ArchivoMultimedia:
    """Valida, guarda en disco y registra la fila en una sola operación coherente."""
    _reject_extra_fields(form_keys, file_keys)
    if "file" not in file_keys:
        raise MediaError("validation_error", "Datos inválidos.", 400, {"file": "Obligatorio."})
    try:
        validated = validate_upload(file_storage)
    except UploadTooLargeError as exc:
        raise MediaError("payload_too_large", str(exc), 413) from exc
    except InvalidImageError as exc:
        raise MediaError("validation_error", str(exc), 400) from exc
    return _persist(validated)


def get_owned_image(archivo_id: UUID) -> ArchivoMultimedia:
    """Metadatos solo del propietario; 404 genérico en otro caso."""
    row = find_owned(archivo_id, current_user.id)
    if row is None:
        raise MediaError("not_found", "Recurso no encontrado.", 404)
    return row


def list_images(page: int, per_page: int) -> tuple[list, int]:
    """Lista paginada de imágenes del usuario autenticado."""
    page = max(page, 1)
    per_page = min(max(per_page, 1), 50)
    return list_owned(current_user.id, page, per_page)


def _reject_extra_fields(form_keys: set[str], file_keys: set[str]) -> None:
    extras = sorted((form_keys | file_keys) - {"file"})
    if extras:
        fields = {name: "Campo no permitido." for name in extras}
        raise MediaError("validation_error", "Datos inválidos.", 400, fields)


def _persist(validated: ValidatedUpload) -> ArchivoMultimedia:
    espacio = find_individual_workspace(current_user.id)
    if espacio is None:
        raise MediaError("server_error", "El usuario no tiene espacio individual.", 500)
    archivo_id = uuid.uuid4()
    key = f"usuarios/{current_user.id}/originales/{archivo_id}{validated.extension}"
    storage = get_storage()
    backend = current_app.config.get("STORAGE_BACKEND", "local")
    try:
        checksum = storage.save(key, io.BytesIO(validated.data))
    except OSError as exc:
        raise MediaError("server_error", "No se pudo guardar el archivo.", 500) from exc
    row = _build_row(archivo_id, espacio.id, key, backend, validated, checksum)
    try:
        save_archivo(row)
        record_event("imagen_subida", "archivo", current_user.id, archivo_id)
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        storage.delete(key)
        raise MediaError("server_error", "No se pudo registrar el archivo.", 500) from exc
    return row


def _build_row(archivo_id, espacio_id, key, backend, validated, checksum):
    """Construye la fila de archivos_multimedia."""
    return ArchivoMultimedia(
        id=archivo_id,
        propietario_id=current_user.id,
        espacio_id=espacio_id,
        tipo="original",
        almacenamiento="local" if backend == "local" else backend,
        ruta_logica=key,
        mime_type=validated.mime_type,
        tamano_bytes=validated.info.size_bytes,
        ancho=validated.info.width,
        alto=validated.info.height,
        checksum_sha256=checksum,
        nombre_original=validated.nombre_original,
    )
