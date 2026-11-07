"""Permisos, listado, descarga y autenticación de imágenes."""

import io

from tests.auth_helpers import csrf_headers, register
from tests.media_helpers import make_image_bytes, registered_client, sha256, upload_png


def test_upload_requires_auth_and_csrf(auth_client, app):
    """Sin sesión → 401; con sesión sin CSRF → 400."""
    png = make_image_bytes("PNG")
    bare_auth = auth_client.post(
        "/api/images/",
        data={"file": (io.BytesIO(png), "a.png")},
        content_type="multipart/form-data",
    )
    assert bare_auth.status_code == 401
    registered_client(auth_client)
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        bare = auth_client.post(
            "/api/images/",
            data={"file": (io.BytesIO(png), "a.png")},
            content_type="multipart/form-data",
        )
        assert bare.status_code == 400
        assert bare.get_json()["error"]["code"] == "csrf_failed"
    finally:
        app.config["WTF_CSRF_ENABLED"] = False


def test_other_user_gets_404(auth_client, app):
    """Otro usuario no ve metadatos ni archivo (404)."""
    registered_client(auth_client, correo="ana@example.com")
    created = upload_png(auth_client).get_json()["image"]["id"]
    auth_client.post("/api/auth/logout", headers=csrf_headers(auth_client))
    register(auth_client, correo="bob@example.com", nombre="Bob")
    assert auth_client.get(f"/api/images/{created}").status_code == 404
    assert auth_client.get(f"/api/images/{created}/file").status_code == 404


def test_download_matches_original_and_headers(auth_client, app):
    """Descarga idéntica al original con cabeceras correctas."""
    registered_client(auth_client)
    original = make_image_bytes("PNG")
    image_id = upload_png(auth_client, data=original).get_json()["image"]["id"]
    response = auth_client.get(f"/api/images/{image_id}/file")
    assert response.status_code == 200
    assert response.data == original
    assert response.mimetype == "image/png"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert "inline" in (response.headers.get("Content-Disposition") or "").lower()
    dl = auth_client.get(f"/api/images/{image_id}/file?download=1")
    assert "attachment" in (dl.headers.get("Content-Disposition") or "").lower()
    assert sha256(response.data) == sha256(original)


def test_list_pagination_only_own(auth_client, app):
    """El listado pagina y solo muestra archivos propios."""
    registered_client(auth_client, correo="ana@example.com")
    for _ in range(3):
        assert upload_png(auth_client).status_code == 201
    auth_client.post("/api/auth/logout", headers=csrf_headers(auth_client))
    register(auth_client, correo="bob@example.com", nombre="Bob")
    upload_png(auth_client)
    listed = auth_client.get("/api/images/?page=1&per_page=2")
    body = listed.get_json()
    assert listed.status_code == 200
    assert body["total"] == 1
    assert len(body["items"]) == 1
