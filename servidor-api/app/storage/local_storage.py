"""Almacenamiento en disco local con escritura atómica."""

import hashlib
import os
import re
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO

from app.storage.base import StorageBackend

_KEY_RE = re.compile(
    r"^usuarios/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/"
    r"originales/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    r"\.(jpg|png)$"
)


class LocalStorage(StorageBackend):
    """Guarda archivos bajo una raíz configurable."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: BinaryIO) -> str:
        """Escribe de forma atómica y calcula el SHA-256."""
        path = self._resolved(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
        try:
            with os.fdopen(fd, "wb") as handle:
                while chunk := data.read(1024 * 64):
                    digest.update(chunk)
                    handle.write(chunk)
            os.replace(tmp_name, path)
        except Exception:
            Path(tmp_name).unlink(missing_ok=True)
            raise
        return digest.hexdigest()

    @contextmanager
    def open(self, key: str) -> Iterator[BinaryIO]:
        """Abre el archivo resuelto para lectura binaria."""
        with self._resolved(key).open("rb") as handle:
            yield handle

    def exists(self, key: str) -> bool:
        """True si el archivo existe dentro de la raíz."""
        return self._resolved(key).is_file()

    def delete(self, key: str) -> None:
        """Borra el archivo si existe."""
        path = self._resolved(key)
        if path.is_file():
            path.unlink()

    def _resolved(self, key: str) -> Path:
        if not _KEY_RE.fullmatch(key):
            raise ValueError("Clave de almacenamiento inválida.")
        path = (self._root / key).resolve()
        if not str(path).startswith(str(self._root) + os.sep) and path != self._root:
            raise ValueError("La ruta sale de la raíz de almacenamiento.")
        return path
