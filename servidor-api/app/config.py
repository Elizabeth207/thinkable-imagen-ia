"""Configuración por entorno. Los secretos salen solo del .env."""

import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]
_API_ROOT = Path(__file__).resolve().parents[1]


def load_env_file() -> None:
    """Carga el .env de la raíz del proyecto si existe."""
    load_dotenv(_ROOT / ".env")


class Config:
    """Valores base compartidos por todos los entornos."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_HEADERS = ["X-CSRFToken", "X-CSRF-Token"]
    RATELIMIT_STORAGE_URI = "memory://"
    LOGIN_RATE_LIMIT = "5 per minute"
    REGISTER_RATE_LIMIT = "10 per minute"
    UPLOAD_RATE_LIMIT = "20 per minute"
    STORAGE_BACKEND = "local"
    MAX_UPLOAD_MB = 10
    MAX_IMAGE_PIXELS = 50_000_000
    MIN_IMAGE_WIDTH = 1
    MIN_IMAGE_HEIGHT = 1


class DevelopmentConfig(Config):
    """Configuración local de desarrollo."""

    DEBUG = True
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True

    def __init__(self) -> None:
        self.SECRET_KEY = _require("SECRET_KEY")
        self.SQLALCHEMY_DATABASE_URI = _require("DATABASE_URL")
        _apply_storage(self)


class TestingConfig(Config):
    """Pruebas contra una base PostgreSQL separada (_test)."""

    TESTING = True
    SECRET_KEY = "test-secret-key"
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    LOGIN_RATE_LIMIT = "1000 per minute"
    REGISTER_RATE_LIMIT = "1000 per minute"
    UPLOAD_RATE_LIMIT = "1000 per minute"

    def __init__(self) -> None:
        self.SQLALCHEMY_DATABASE_URI = test_database_url(_require("DATABASE_URL"))
        _apply_storage(self)


def get_config(name: str | None = None) -> type[Config] | Config:
    """Devuelve la clase o instancia de configuración pedida."""
    chosen = (name or os.environ.get("FLASK_ENV", "development")).strip().lower()
    if chosen == "testing":
        return TestingConfig()
    if chosen == "development":
        return DevelopmentConfig()
    raise ValueError(f"Entorno desconocido: {chosen}")


def test_database_url(database_url: str) -> str:
    """Deriva la URL de la base de pruebas sin tocar la de desarrollo."""
    parts = urlsplit(database_url)
    path = parts.path.rstrip("/") or "/postgres"
    name = path.rsplit("/", 1)[-1]
    if not name.endswith("_test"):
        name = f"{name}_test"
    return urlunsplit((parts.scheme, parts.netloc, f"/{name}", parts.query, parts.fragment))


def _apply_storage(cfg: Config) -> None:
    cfg.STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "local").strip() or "local"
    root = os.environ.get("STORAGE_ROOT", "").strip()
    cfg.STORAGE_ROOT = root or str(_API_ROOT / "storage")
    cfg.MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", str(Config.MAX_UPLOAD_MB)))
    cfg.MAX_CONTENT_LENGTH = cfg.MAX_UPLOAD_MB * 1024 * 1024


def _require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Falta la variable de entorno {name}.")
    return value
