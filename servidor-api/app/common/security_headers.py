"""Cabeceras de seguridad HTTP."""

from flask import Flask, request


def register_security_headers(app: Flask) -> None:
    """Añade cabeceras de seguridad a todas las respuestas."""

    @app.after_request
    def _add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if request.path.startswith("/api/auth"):
            response.headers["Cache-Control"] = "no-store"
        return response
