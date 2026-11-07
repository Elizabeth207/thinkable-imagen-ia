"""Validación de imágenes subidas (contenido real con Pillow)."""

import io
from dataclasses import dataclass

from flask import current_app
from motor_ia.errors import InvalidImageError
from motor_ia.validation.image_checks import ALLOWED_FORMATS, ImageInfo
from PIL import Image, ImageFile, UnidentifiedImageError

ImageFile.LOAD_TRUNCATED_IMAGES = False

_MIME = {"JPEG": "image/jpeg", "PNG": "image/png"}
_EXT = {"JPEG": ".jpg", "PNG": ".png"}


class UploadTooLargeError(Exception):
    """El archivo supera MAX_UPLOAD_MB."""


@dataclass(frozen=True)
class ValidatedUpload:
    """Resultado de validar una subida aceptada."""

    info: ImageInfo
    mime_type: str
    extension: str
    data: bytes
    nombre_original: str | None


def validate_upload(file_storage) -> ValidatedUpload:
    """Valida el contenido real; el mime sale del formato detectado."""
    if file_storage is None:
        raise InvalidImageError("Falta el archivo en el campo file.")
    raw = file_storage.read()
    max_bytes = int(current_app.config["MAX_UPLOAD_MB"]) * 1024 * 1024
    if len(raw) == 0:
        raise InvalidImageError("El archivo está vacío.")
    if len(raw) > max_bytes:
        raise UploadTooLargeError("El archivo supera el tamaño máximo permitido.")
    info = _inspect_bytes(raw)
    return ValidatedUpload(
        info=info,
        mime_type=_MIME[info.image_format],
        extension=_EXT[info.image_format],
        data=raw,
        nombre_original=_sanitize_name(getattr(file_storage, "filename", None)),
    )


def _inspect_bytes(raw: bytes) -> ImageInfo:
    max_pixels = int(current_app.config["MAX_IMAGE_PIXELS"])
    min_w = int(current_app.config["MIN_IMAGE_WIDTH"])
    min_h = int(current_app.config["MIN_IMAGE_HEIGHT"])
    Image.MAX_IMAGE_PIXELS = max_pixels
    try:
        with Image.open(io.BytesIO(raw)) as image:
            image.verify()
        with Image.open(io.BytesIO(raw)) as image:
            width, height = image.size
            fmt = image.format or ""
    except Image.DecompressionBombError as exc:
        raise InvalidImageError("La imagen supera el límite de píxeles.") from exc
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError("El contenido no es una imagen válida.") from exc
    if fmt not in ALLOWED_FORMATS:
        raise InvalidImageError("Solo se permiten JPEG y PNG.")
    if width < min_w or height < min_h:
        raise InvalidImageError("Las dimensiones de la imagen son demasiado pequeñas.")
    return ImageInfo(width, height, len(raw), fmt)


def _sanitize_name(name: str | None) -> str | None:
    if not name:
        return None
    base = name.replace("\\", "/").split("/")[-1]
    cleaned = "".join(ch for ch in base if ch.isprintable() and ch not in '<>:"|?*')
    cleaned = cleaned.strip().strip(".")[:255]
    return cleaned or None
