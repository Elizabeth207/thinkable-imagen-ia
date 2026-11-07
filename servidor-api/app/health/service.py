"""Comprueba que la base de datos responda."""

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db


def check_database() -> dict[str, str]:
    """Ejecuta SELECT 1. No expone detalles internos si falla."""
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except SQLAlchemyError:
        return {"status": "unavailable", "database": "unavailable"}
