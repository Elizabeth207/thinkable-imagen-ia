"""Decoradores de autenticación y roles (siempre en el backend)."""

from collections.abc import Callable
from functools import wraps

from flask_login import current_user

from app.common.responses import error_response


def login_required_json(view: Callable):
    """Exige sesión activa y cuenta activa; 401 JSON si no."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return error_response("unauthorized", "Autenticación requerida.", 401)
        if getattr(current_user, "estado", None) != "activo":
            return error_response("unauthorized", "Autenticación requerida.", 401)
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles: str):
    """Exige autenticación y uno de los roles indicados."""

    def decorator(view: Callable):
        @wraps(view)
        @login_required_json
        def wrapped(*args, **kwargs):
            if current_user.rol_global not in roles:
                return error_response("forbidden", "No tienes permiso.", 403)
            return view(*args, **kwargs)

        return wrapped

    return decorator
