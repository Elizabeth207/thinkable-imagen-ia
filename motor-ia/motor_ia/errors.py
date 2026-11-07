"""Errores del paquete. Los mensajes no incluyen secretos."""


class MotorIAError(Exception):
    """Error base de la mejora de imágenes."""


class MissingApiKeyError(MotorIAError):
    """Falta la clave del proveedor en el entorno."""


class InvalidImageError(MotorIAError):
    """La imagen no pasó las comprobaciones locales."""


class ProviderUnavailableError(MotorIAError):
    """El proveedor no respondió o la respuesta no es usable."""


class JobFailedError(MotorIAError):
    """El trabajo falló. No se vuelve a enviar solo."""


class JobTimeoutError(MotorIAError):
    """Se agotó la espera. El trabajo no se reenvía."""
