"""Ayudas para pruebas de subida de imágenes."""

import io
import hashlib

from PIL import Image

from tests.auth_helpers import csrf_headers, register


def make_image_bytes(fmt: str = "PNG", size=(32, 32), color=(10, 20, 30)) -> bytes:
    """Genera bytes de una imagen mínima válida."""
    image = Image.new("RGB", size, color=color)
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def sha256(data: bytes) -> str:
    """Hash hex de los bytes."""
    return hashlib.sha256(data).hexdigest()


def upload_png(client, filename: str = "foto.png", **kwargs):
    """Registra si hace falta y sube un PNG."""
    data = kwargs.pop("data", None) or make_image_bytes("PNG")
    return client.post(
        "/api/images/",
        data={"file": (io.BytesIO(data), filename)},
        content_type="multipart/form-data",
        headers=csrf_headers(client),
    )


def upload_jpeg(client, filename: str = "foto.jpg"):
    """Sube un JPEG válido."""
    data = make_image_bytes("JPEG")
    return client.post(
        "/api/images/",
        data={"file": (io.BytesIO(data), filename)},
        content_type="multipart/form-data",
        headers=csrf_headers(client),
    )


def registered_client(client, correo: str = "ana@example.com"):
    """Asegura un usuario autenticado tras el registro."""
    register(client, correo=correo)
    return client
