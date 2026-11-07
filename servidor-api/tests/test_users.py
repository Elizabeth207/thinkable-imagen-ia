"""Restricciones de la tabla usuarios."""

import pytest
from sqlalchemy.exc import IntegrityError

from tests.builders import make_usuario


def test_usuario_valido(db_session):
    """Acepta un usuario con datos válidos."""
    user = make_usuario()
    db_session.commit()
    assert user.id is not None
    assert user.rol_global == "usuario"


def test_correo_unico_sin_importar_mayusculas(db_session):
    """Rechaza el mismo correo con distinta capitalización."""
    make_usuario(correo="Ana@Example.com")
    db_session.commit()
    with pytest.raises(IntegrityError):
        make_usuario(nombre="Otra", correo="ana@example.com")


def test_estado_invalido_rechazado(db_session):
    """Rechaza un estado fuera del CHECK."""
    with pytest.raises(IntegrityError):
        make_usuario(estado="bloqueado")


def test_rol_global_invalido_rechazado(db_session):
    """Rechaza un rol_global fuera del CHECK."""
    with pytest.raises(IntegrityError):
        make_usuario(rol_global="superadmin")
