"""Rutas de autenticación. Solo reciben y responden."""

from flask import Blueprint, current_app, request
from flask_login import current_user
from flask_wtf.csrf import generate_csrf

from app.auth import service
from app.auth.permissions import login_required_json
from app.auth.errors import AuthError
from app.auth.validators import (
    validate_change_password,
    validate_login,
    validate_register,
)
from app.common.responses import error_response, success_response
from app.extensions import limiter
from app.users.serializers import serialize_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.get("/csrf")
def csrf_token():
    """Devuelve un token CSRF para peticiones que modifican datos."""
    return success_response({"csrf_token": generate_csrf()})


@auth_bp.post("/register")
@limiter.limit(lambda: current_app.config["REGISTER_RATE_LIMIT"])
def register():
    """Crea una cuenta de usuario."""
    data, fields = validate_register(request.get_json(silent=True) or {})
    if fields:
        return error_response("validation_error", "Datos inválidos.", 400, fields)
    try:
        user = service.register_user(data["nombre"], data["correo"], data["contraseña"])
    except AuthError as exc:
        return error_response(exc.code, exc.message, exc.status_code, exc.fields)
    return success_response({"user": serialize_user(user)}, 201)


@auth_bp.post("/login")
@limiter.limit(lambda: current_app.config["LOGIN_RATE_LIMIT"])
def login():
    """Inicia sesión con correo y contraseña."""
    data, fields = validate_login(request.get_json(silent=True) or {})
    if fields:
        return error_response("validation_error", "Datos inválidos.", 400, fields)
    try:
        user = service.authenticate(data["correo"], data["contraseña"])
    except AuthError as exc:
        return error_response(exc.code, exc.message, exc.status_code, exc.fields)
    return success_response({"user": serialize_user(user)})


@auth_bp.post("/logout")
@login_required_json
def logout():
    """Cierra la sesión actual."""
    service.logout_current()
    return success_response({"ok": True})


@auth_bp.get("/me")
@login_required_json
def me():
    """Devuelve el usuario autenticado."""
    return success_response({"user": serialize_user(current_user)})


@auth_bp.post("/change-password")
@login_required_json
def change_password():
    """Cambia la contraseña exigiendo la actual."""
    data, fields = validate_change_password(
        request.get_json(silent=True) or {},
        current_user.correo,
    )
    if fields:
        return error_response("validation_error", "Datos inválidos.", 400, fields)
    try:
        service.change_password(
            current_user,
            data["contraseña_actual"],
            data["contraseña_nueva"],
        )
    except AuthError as exc:
        return error_response(exc.code, exc.message, exc.status_code, exc.fields)
    return success_response({"ok": True})
