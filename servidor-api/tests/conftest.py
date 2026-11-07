"""Fixtures compartidas de las pruebas del backend."""

import os

import pytest
from flask_migrate import upgrade

from app import create_app
from app.config import load_env_file
from app.extensions import db, limiter
from tests.db_support import ensure_test_database, truncate_all


@pytest.fixture(scope="session")
def app():
    """App de prueba contra la base PostgreSQL *_test."""
    load_env_file()
    ensure_test_database(os.environ["DATABASE_URL"])
    application = create_app("testing")
    with application.app_context():
        upgrade()
    yield application


@pytest.fixture()
def client(app):
    """Cliente HTTP. Preferir auth_client si hace falta sesión/CSRF."""
    return app.test_client()


@pytest.fixture()
def auth_client(app, tmp_path):
    """Cliente con BD limpia, storage temporal y sin app_context externo."""
    app.config["STORAGE_ROOT"] = str(tmp_path / "storage")
    app.config["STORAGE_BACKEND"] = "local"
    with app.app_context():
        limiter.reset()
        truncate_all()
    client = app.test_client()
    yield client
    with app.app_context():
        db.session.remove()
        truncate_all()
        limiter.reset()


@pytest.fixture()
def db_session(app):
    """Sesión SQLAlchemy para pruebas de modelos (sin cliente HTTP)."""
    with app.app_context():
        limiter.reset()
        truncate_all()
        yield db.session
        db.session.rollback()
        truncate_all()
        limiter.reset()
