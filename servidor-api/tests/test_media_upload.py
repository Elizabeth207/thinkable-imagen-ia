"""Subida válida y registro en disco/base."""

from pathlib import Path

from sqlalchemy import select

from app.audit.models import Auditoria
from app.extensions import db
from app.media.models import ArchivoMultimedia
from tests.media_helpers import (
    make_image_bytes,
    registered_client,
    sha256,
    upload_jpeg,
    upload_png,
)


def test_upload_png_and_jpeg(auth_client, app):
    """PNG y JPEG crean archivo, fila, SHA-256 y mime correctos."""
    registered_client(auth_client)
    png = make_image_bytes("PNG")
    response = upload_png(auth_client, data=png)
    assert response.status_code == 201
    body = response.get_json()["image"]
    assert body["mime_type"] == "image/png"
    assert body["checksum_sha256"] == sha256(png)
    assert body["nombre_original"] == "foto.png"
    jpeg = upload_jpeg(auth_client)
    assert jpeg.status_code == 201
    assert jpeg.get_json()["image"]["mime_type"] == "image/jpeg"
    with app.app_context():
        rows = db.session.scalars(select(ArchivoMultimedia)).all()
        assert len(rows) == 2
        root = Path(app.config["STORAGE_ROOT"])
        for row in rows:
            assert (root / row.ruta_logica).is_file()
        actions = db.session.scalars(select(Auditoria.accion)).all()
        assert actions.count("imagen_subida") == 2


def test_upload_rejects_extra_fields(auth_client, app):
    """Campos extra como espacio_id → 400 validation_error."""
    registered_client(auth_client)
    from tests.auth_helpers import csrf_headers
    import io

    response = auth_client.post(
        "/api/images/",
        data={
            "file": (io.BytesIO(make_image_bytes("PNG")), "a.png"),
            "espacio_id": "x",
            "propietario_id": "y",
        },
        content_type="multipart/form-data",
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 400
    fields = response.get_json()["error"]["fields"]
    assert "espacio_id" in fields and "propietario_id" in fields
