"""Coherencia disco/base y backend Dropbox."""

from pathlib import Path
from unittest.mock import patch

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.media.models import ArchivoMultimedia
from app.storage.factory import StorageNotImplementedError, get_storage
from tests.media_helpers import registered_client, upload_png


def test_storage_failure_leaves_no_db_row(auth_client, app):
    """Si falla el guardado en disco, no queda fila."""
    registered_client(auth_client)
    with patch("app.media.service.get_storage") as mocked:
        mocked.return_value.save.side_effect = OSError("disk full")
        response = upload_png(auth_client)
    assert response.status_code == 500
    with app.app_context():
        assert db.session.scalar(select(func.count()).select_from(ArchivoMultimedia)) == 0


def test_db_failure_removes_saved_file(auth_client, app):
    """Si falla la base tras guardar, se elimina el archivo."""
    registered_client(auth_client)
    root = Path(app.config["STORAGE_ROOT"])
    with patch("app.media.service.save_archivo", side_effect=SQLAlchemyError("db down")):
        response = upload_png(auth_client)
    assert response.status_code == 500
    with app.app_context():
        assert db.session.scalar(select(func.count()).select_from(ArchivoMultimedia)) == 0
    assert not any(path.is_file() for path in root.rglob("*"))


def test_dropbox_backend_not_implemented(auth_client, app):
    """STORAGE_BACKEND=dropbox falla con mensaje claro."""
    app.config["STORAGE_BACKEND"] = "dropbox"
    try:
        with app.app_context():
            try:
                get_storage(app)
                raise AssertionError("debía fallar")
            except StorageNotImplementedError as exc:
                assert "dropbox" in str(exc).lower()
        registered_client(auth_client)
        response = upload_png(auth_client)
        assert response.status_code == 501
        assert response.get_json()["error"]["code"] == "not_implemented"
    finally:
        app.config["STORAGE_BACKEND"] = "local"


def test_migration_nombre_original_roundtrip(app):
    """La migración de nombre_original sube y baja."""
    from flask_migrate import downgrade, upgrade

    with app.app_context():
        downgrade(revision="522a5f5764ba")
        upgrade()
