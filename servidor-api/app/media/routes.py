"""Rutas de imágenes. Solo reciben y responden."""

import io
from uuid import UUID

from flask import Blueprint, current_app, request, send_file
from flask_login import current_user

from app.auth.permissions import login_required_json
from app.common.responses import error_response, success_response
from app.extensions import limiter
from app.media import service
from app.media.serializers import serialize_archivo
from app.media.errors import MediaError
from app.storage.factory import StorageNotImplementedError, get_storage

media_bp = Blueprint("media", __name__, url_prefix="/api/images")


@media_bp.post("/")
@login_required_json
@limiter.limit(
    lambda: current_app.config["UPLOAD_RATE_LIMIT"],
    key_func=lambda: str(current_user.id),
)
def upload():
    """Sube una imagen al espacio individual del usuario."""
    try:
        row = service.upload_image(
            request.files.get("file"),
            set(request.form.keys()),
            set(request.files.keys()),
        )
    except StorageNotImplementedError as exc:
        return error_response("not_implemented", str(exc), 501)
    except MediaError as exc:
        return error_response(exc.code, exc.message, exc.status_code, exc.fields)
    return success_response({"image": serialize_archivo(row)}, 201)


@media_bp.get("/")
@login_required_json
def list_images():
    """Lista paginada de imágenes del usuario."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    items, total = service.list_images(page, per_page)
    return success_response(
        {
            "items": [serialize_archivo(item) for item in items],
            "page": max(page, 1),
            "per_page": min(max(per_page, 1), 50),
            "total": total,
        }
    )


@media_bp.get("/<uuid:image_id>")
@login_required_json
def detail(image_id: UUID):
    """Metadatos de una imagen propia."""
    try:
        row = service.get_owned_image(image_id)
    except MediaError as exc:
        return error_response(exc.code, exc.message, exc.status_code, exc.fields)
    return success_response({"image": serialize_archivo(row)})


@media_bp.get("/<uuid:image_id>/file")
@login_required_json
def download(image_id: UUID):
    """Entrega el archivo; ?download=1 fuerza attachment."""
    try:
        row = service.get_owned_image(image_id)
        with get_storage().open(row.ruta_logica) as handle:
            payload = io.BytesIO(handle.read())
    except MediaError as exc:
        return error_response(exc.code, exc.message, exc.status_code, exc.fields)
    download = request.args.get("download") == "1"
    name = row.nombre_original or f"{row.id}.bin"
    response = send_file(
        payload,
        mimetype=row.mime_type,
        as_attachment=download,
        download_name=name,
        max_age=0,
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
