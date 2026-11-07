"""Comando de consola para crear un administrador general."""

import click
from flask import Flask
from sqlalchemy.exc import IntegrityError

from app.audit.service import record_event
from app.auth.passwords import hash_password, password_policy_error
from app.auth.validators import _normalize_email
from app.extensions import db
from app.users.models import Usuario
from app.users.repository import find_by_email, save
from app.workspaces.repository import create_individual_workspace


def register_cli(app: Flask) -> None:
    """Registra el comando flask create-admin."""

    @app.cli.command("create-admin")
    def create_admin() -> None:
        """Crea un usuario con rol admin_general y su espacio."""
        correo_raw = click.prompt("Correo")
        nombre = click.prompt("Nombre").strip()
        password = click.prompt("Contraseña", hide_input=True, confirmation_prompt=True)
        correo, err = _normalize_email(correo_raw)
        if err or not nombre:
            raise click.ClickException(err or "El nombre es obligatorio.")
        policy = password_policy_error(password, correo or "")
        if policy:
            raise click.ClickException(policy)
        if find_by_email(correo) is not None:
            raise click.ClickException("El correo ya está registrado.")
        _persist_admin(nombre, correo, password)
        click.echo("Administrador creado.")


def _persist_admin(nombre: str, correo: str, password: str) -> None:
    """Guarda el admin, espacio y membresía en una transacción."""
    user = Usuario(
        nombre=nombre,
        correo=correo,
        password_hash=hash_password(password),
        estado="activo",
        rol_global="admin_general",
    )
    try:
        save(user)
        create_individual_workspace(user.id, nombre)
        record_event("admin_creado", "usuario", user.id, user.id)
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise click.ClickException("El correo ya está registrado.") from exc
