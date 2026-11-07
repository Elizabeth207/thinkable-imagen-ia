"""Errores de negocio del dominio media."""


class MediaError(Exception):
    """Error de media con código HTTP y campos opcionales."""

    def __init__(self, code: str, message: str, status_code: int, fields=None) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.fields = fields
