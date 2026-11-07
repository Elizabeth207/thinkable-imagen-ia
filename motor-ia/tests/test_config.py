"""Pruebas de configuración. No llaman al proveedor."""

import pytest

from motor_ia.config import load_settings
from motor_ia.errors import MissingApiKeyError, MotorIAError


def test_missing_key_fails_clearly(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin clave, el mensaje nombra la variable y no inventa un valor."""
    monkeypatch.delenv("IMAGE_PROVIDER_API_KEY", raising=False)
    with pytest.raises(MissingApiKeyError, match="IMAGE_PROVIDER_API_KEY"):
        load_settings()


def test_settings_hide_the_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """La representación no debe mostrar la clave."""
    monkeypatch.setenv("IMAGE_PROVIDER_API_KEY", "secreto-de-prueba")
    settings = load_settings()
    assert settings.api_token == "secreto-de-prueba"
    assert "secreto-de-prueba" not in repr(settings)
    assert settings.preset == "gfpgan"
    assert settings.poll_interval_seconds == 0.5


def test_invalid_poll_interval(monkeypatch: pytest.MonkeyPatch) -> None:
    """Un intervalo que no es un número positivo se rechaza."""
    monkeypatch.setenv("IMAGE_PROVIDER_API_KEY", "secreto-de-prueba")
    monkeypatch.setenv("IMAGE_PROVIDER_POLL_INTERVAL_SECONDS", "0")
    with pytest.raises(MotorIAError, match="mayor que cero"):
        load_settings()
