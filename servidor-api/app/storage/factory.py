"""Selecciona el backend de almacenamiento según configuración."""

from pathlib import Path

from flask import Flask, current_app

from app.storage.base import StorageBackend
from app.storage.local_storage import LocalStorage


class StorageNotImplementedError(RuntimeError):
    """Backend pedido todavía no disponible."""


def get_storage(app: Flask | None = None) -> StorageBackend:
    """Devuelve el backend configurado o falla con mensaje claro."""
    flask_app = app if app is not None else current_app
    backend = str(flask_app.config.get("STORAGE_BACKEND", "local")).strip().lower()
    if backend == "local":
        return LocalStorage(Path(flask_app.config["STORAGE_ROOT"]))
    if backend == "dropbox":
        raise StorageNotImplementedError(
            "El backend Dropbox no está implementado todavía."
        )
    raise StorageNotImplementedError(f"Backend de almacenamiento desconocido: {backend}")
