"""Lee la configuración del proveedor desde el entorno."""

import os

from motor_ia.errors import MissingApiKeyError, MotorIAError
from motor_ia.models import EnhanceOptions


class Settings:
    """Valores necesarios para hablar con el proveedor."""

    def __init__(
        self,
        api_token: str,
        preset: str,
        poll_interval_seconds: float,
        max_wait_seconds: float,
        base_url: str | None,
    ) -> None:
        self.api_token = api_token
        self.preset = preset
        self.poll_interval_seconds = poll_interval_seconds
        self.max_wait_seconds = max_wait_seconds
        self.base_url = base_url

    def __repr__(self) -> str:
        return (
            "Settings(api_token='***', "
            f"preset={self.preset!r}, "
            f"poll_interval_seconds={self.poll_interval_seconds}, "
            f"max_wait_seconds={self.max_wait_seconds}, "
            f"base_url={self.base_url!r})"
        )

    def to_options(self) -> EnhanceOptions:
        """Copia los ajustes de sondeo, sin la clave."""
        return EnhanceOptions(
            self.preset,
            self.poll_interval_seconds,
            self.max_wait_seconds,
        )


def load_settings(preset: str | None = None) -> Settings:
    """Valida la clave y los tiempos. Falla si la clave no está."""
    token = os.environ.get("IMAGE_PROVIDER_API_KEY", "").strip()
    if not token:
        raise MissingApiKeyError(
            "Falta IMAGE_PROVIDER_API_KEY. Defínela en el .env de la raíz."
        )
    chosen = (preset or os.environ.get("IMAGE_PROVIDER_PRESET", "gfpgan")).strip()
    if not chosen:
        raise MotorIAError("IMAGE_PROVIDER_PRESET no puede estar vacío.")
    base_url = os.environ.get("IMAGE_PROVIDER_BASE_URL", "").strip() or None
    return Settings(
        token,
        chosen,
        _positive_float("IMAGE_PROVIDER_POLL_INTERVAL_SECONDS", "0.5"),
        _positive_float("IMAGE_PROVIDER_MAX_WAIT_SECONDS", "180"),
        base_url,
    )


def _positive_float(name: str, default: str) -> float:
    raw = os.environ.get(name, default).strip()
    try:
        value = float(raw)
    except ValueError as exc:
        raise MotorIAError(f"{name} debe ser un número.") from exc
    if value <= 0:
        raise MotorIAError(f"{name} debe ser mayor que cero.")
    return value
