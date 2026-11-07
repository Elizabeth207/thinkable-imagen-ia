"""Validación de formatos, tamaño y píxeles."""

import io

from tests.auth_helpers import csrf_headers
from tests.media_helpers import make_image_bytes, registered_client, upload_png


def test_text_renamed_as_png_rejected(auth_client, app):
    """Texto renombrado a .png → 400."""
    registered_client(auth_client)
    response = auth_client.post(
        "/api/images/",
        data={"file": (io.BytesIO(b"not-an-image"), "fake.png")},
        content_type="multipart/form-data",
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 400


def test_gif_webp_rejected(auth_client, app):
    """GIF y WEBP no permitidos → 400."""
    registered_client(auth_client)
    samples = [("a.gif", make_image_bytes("GIF"))]
    try:
        samples.append(("a.webp", make_image_bytes("WEBP")))
    except Exception:
        samples.append(("a.webp", b"RIFF\x00\x00\x00\x00WEBPVP8 "))
    for name, data in samples:
        response = auth_client.post(
            "/api/images/",
            data={"file": (io.BytesIO(data), name)},
            content_type="multipart/form-data",
            headers=csrf_headers(auth_client),
        )
        assert response.status_code == 400


def test_empty_file_rejected(auth_client, app):
    """Archivo vacío → 400."""
    registered_client(auth_client)
    response = auth_client.post(
        "/api/images/",
        data={"file": (io.BytesIO(b""), "empty.png")},
        content_type="multipart/form-data",
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 400


def test_oversize_returns_413(auth_client, app):
    """Por encima de MAX_UPLOAD_MB → 413 JSON."""
    app.config["MAX_UPLOAD_MB"] = 1
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
    registered_client(auth_client)
    big = b"x" * (1024 * 1024 + 10)
    response = auth_client.post(
        "/api/images/",
        data={"file": (io.BytesIO(big), "big.png")},
        content_type="multipart/form-data",
        headers=csrf_headers(auth_client),
    )
    assert response.status_code == 413
    assert response.get_json()["error"]["code"] == "payload_too_large"
    app.config["MAX_UPLOAD_MB"] = 10


def test_pixel_limit_rejected(auth_client, app):
    """Imagen que supera el límite de píxeles → 400."""
    app.config["MAX_IMAGE_PIXELS"] = 100
    registered_client(auth_client)
    data = make_image_bytes("PNG", size=(50, 50))
    response = upload_png(auth_client, data=data)
    assert response.status_code == 400
    app.config["MAX_IMAGE_PIXELS"] = 50_000_000


def test_traversal_name_does_not_escape(auth_client, app):
    """../../x.png no escribe fuera de la raíz ni altera la clave."""
    registered_client(auth_client)
    response = upload_png(auth_client, filename="../../x.png")
    assert response.status_code == 201
    image = response.get_json()["image"]
    assert ".." not in image["id"]
    root = app.config["STORAGE_ROOT"]
    from pathlib import Path
    from sqlalchemy import select
    from app.extensions import db
    from app.media.models import ArchivoMultimedia

    with app.app_context():
        row = db.session.scalars(select(ArchivoMultimedia)).one()
        path = Path(root) / row.ruta_logica
        assert path.is_file()
        assert path.resolve().is_relative_to(Path(root).resolve())
        assert row.nombre_original == "x.png"
