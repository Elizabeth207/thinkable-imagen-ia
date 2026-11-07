"""Utilidades para la base de pruebas PostgreSQL."""

from urllib.parse import urlsplit, urlunsplit

import psycopg
from sqlalchemy import text

from app.config import test_database_url
from app.extensions import db


def to_psycopg_url(sqlalchemy_url: str) -> str:
    """Convierte la URL de SQLAlchemy a formato psycopg."""
    return sqlalchemy_url.replace("postgresql+psycopg://", "postgresql://", 1)


def ensure_test_database(database_url: str) -> str:
    """Crea la base *_test si no existe. No toca la de desarrollo."""
    test_url = test_database_url(database_url)
    parts = urlsplit(to_psycopg_url(test_url))
    name = parts.path.lstrip("/")
    admin = urlunsplit((parts.scheme, parts.netloc, "/postgres", "", ""))
    with psycopg.connect(admin, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))
            if cur.fetchone() is None:
                cur.execute(f'CREATE DATABASE "{name}"')
    return test_url


def truncate_all() -> None:
    """Vacía las tablas de negocio preservando el esquema."""
    db.session.execute(
        text(
            "TRUNCATE auditoria, procesamientos_ia, archivos_multimedia, "
            "membresias_espacio, espacios_trabajo, proveedores_ia, usuarios "
            "CASCADE"
        )
    )
    db.session.commit()
