"""Errores de negocio de autenticación."""


class AuthError(Exception):
    """Error de autenticación con código HTTP y campos opcionales."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        fields: dict[str, str] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.fields = fields
