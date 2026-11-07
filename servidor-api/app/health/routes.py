"""Rutas del dominio de salud. Sin lógica de negocio."""

from flask import Blueprint

from app.common.responses import error_response, success_response
from app.health.service import check_database

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health():
    """Estado general y de la base de datos."""
    payload = check_database()
    if payload["database"] != "ok":
        return error_response(
            "database_unavailable",
            "La base de datos no está disponible.",
            503,
        )
    return success_response(payload)
