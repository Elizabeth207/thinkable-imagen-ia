"""Respuestas JSON con formato uniforme."""

from typing import Any

from flask import jsonify


def success_response(payload: dict[str, Any], status_code: int = 200):
    """Devuelve un JSON de éxito con el código HTTP indicado."""
    return jsonify(payload), status_code


def error_response(
    code: str,
    message: str,
    status_code: int,
    fields: dict[str, str] | None = None,
):
    """Devuelve un error JSON; opcionalmente con detalle por campo."""
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if fields:
        body["error"]["fields"] = fields
    return jsonify(body), status_code
