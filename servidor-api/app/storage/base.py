"""Contrato de un backend de almacenamiento de archivos."""

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import BinaryIO


class StorageBackend(ABC):
    """Operaciones mínimas sobre objetos binarios."""

    @abstractmethod
    def save(self, key: str, data: BinaryIO) -> str:
        """Guarda el flujo en la clave y devuelve el SHA-256 hex."""

    @abstractmethod
    def open(self, key: str) -> AbstractContextManager[BinaryIO]:
        """Abre el objeto para lectura."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Indica si la clave existe."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Elimina la clave si existe."""
