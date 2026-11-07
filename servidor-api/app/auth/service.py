"""Lógica de registro, autenticación y cambio de contraseña."""

from flask import session
from flask_login import login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.audit.service import record_event
from app.auth.errors import AuthError
from app.auth.passwords import hash_password, verify_or_dummy, verify_password
from app.extensions import db
from app.users.models import Usuario
from app.users.repository import find_by_email, save
from app.workspaces.repository import create_individual_workspace


def register_user(nombre: str, correo: str, password: str) -> Usuario:
    """Crea usuario, espacio individual y membresía en una transacción."""
    if find_by_email(correo) is not None:
        raise AuthError("email_taken", "El correo ya está registrado.", 409)
    user = Usuario(
        nombre=nombre,
        correo=correo,
        password_hash=hash_password(password),
        estado="activo",
        rol_global="usuario",
    )
    try:
        save(user)
        create_individual_workspace(user.id, nombre)
        record_event("usuario_registrado", "usuario", user.id, user.id)
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise AuthError("email_taken", "El correo ya está registrado.", 409) from exc
    _start_session(user)
    return user


def authenticate(correo: str, password: str) -> Usuario:
    """Valida credenciales y abre sesión (sin remember)."""
    user = find_by_email(correo)
    stored = user.password_hash if user is not None else None
    valid = verify_or_dummy(stored, password)
    if user is None or not valid:
        if user is not None:
            record_event("login_failed", "usuario", user.id, user.id)
            db.session.commit()
        raise AuthError("invalid_credentials", "credenciales inválidas", 401)
    if user.estado != "activo":
        raise AuthError("account_inactive", "La cuenta está inactiva.", 403)
    _start_session(user)
    record_event("login_ok", "usuario", user.id, user.id)
    db.session.commit()
    return user


def logout_current() -> None:
    """Cierra la sesión actual."""
    logout_user()
    session.clear()


def change_password(user: Usuario, current: str, new: str) -> None:
    """Cambia la contraseña si la actual es correcta y la nueva es distinta."""
    if not verify_password(user.password_hash, current):
        raise AuthError(
            "validation_error",
            "No se pudo cambiar la contraseña.",
            400,
            {"contraseña_actual": "La contraseña actual no es correcta."},
        )
    if verify_password(user.password_hash, new):
        raise AuthError(
            "same_password",
            "La nueva contraseña debe ser distinta de la actual.",
            400,
        )
    user.password_hash = hash_password(new)
    save(user)
    record_event("password_changed", "usuario", user.id, user.id)
    db.session.commit()


def _start_session(user: Usuario) -> None:
    """Abre sesión tras limpiar la cookie de esta petición."""
    session.clear()
    login_user(user, remember=False)
    session.permanent = True
