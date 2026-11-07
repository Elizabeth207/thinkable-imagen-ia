"""Manejadores de error con el mismo formato JSON."""

from flask import Flask
from flask_limiter.errors import RateLimitExceeded
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException

from app.common.responses import error_response


def register_error_handlers(app: Flask) -> None:
    """Registra manejadores HTTP, CSRF y límite de intentos."""
    app.register_error_handler(404, _not_found)
    app.register_error_handler(413, _payload_too_large)
    app.register_error_handler(500, _server_error)
    app.register_error_handler(CSRFError, _csrf_failed)
    app.register_error_handler(RateLimitExceeded, _rate_limited)
    app.register_error_handler(HTTPException, _http_error)
    app.register_error_handler(Exception, _unhandled)


def _not_found(_error: Exception):
    """Responde cuando la ruta no existe."""
    return error_response("not_found", "Recurso no encontrado.", 404)


def _server_error(_error: Exception):
    """Responde ante un fallo interno no previsto."""
    return error_response("server_error", "Error interno del servidor.", 500)


def _payload_too_large(_error: Exception):
    """Cuerpo o archivo por encima de MAX_CONTENT_LENGTH."""
    return error_response(
        "payload_too_large",
        "El archivo supera el tamaño máximo permitido.",
        413,
    )


def _csrf_failed(_error: CSRFError):
    """Token CSRF ausente o inválido."""
    return error_response("csrf_failed", "Token CSRF inválido o ausente.", 400)


def _rate_limited(error: RateLimitExceeded):
    """Demasiados intentos; incluye Retry-After cuando el límite lo aporta."""
    response, status = error_response(
        "rate_limited",
        "Demasiados intentos. Intenta más tarde.",
        429,
    )
    retry_after = getattr(error, "retry_after", None)
    if retry_after is not None:
        response.headers["Retry-After"] = str(int(retry_after))
    return response, status


def _http_error(error: HTTPException):
    """Traduce excepciones HTTP de Werkzeug al formato común."""
    code = (error.name or "http_error").lower().replace(" ", "_")
    message = error.description or "Error en la petición."
    return error_response(code, message, error.code or 500)


def _unhandled(_error: Exception):
    """Captura cualquier excepción no tipada como HTTP."""
    return error_response("server_error", "Error interno del servidor.", 500)
