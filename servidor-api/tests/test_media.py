"""Restricciones de archivos_multimedia."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.users.models import Usuario
from tests.builders import make_archivo, make_espacio, make_usuario


def test_archivo_valido(db_session):
    """Acepta un archivo multimedia con datos válidos."""
    user = make_usuario()
    espacio = make_espacio(user.id)
    archivo = make_archivo(user.id, espacio.id)
    db_session.commit()
    assert archivo.tamano_bytes == 1024


def test_no_borrar_usuario_con_archivos(db_session):
    """RESTRICT impide borrar un usuario que aún tiene archivos."""
    user = make_usuario()
    espacio = make_espacio(user.id)
    make_archivo(user.id, espacio.id)
    db_session.commit()
    db_session.delete(db_session.get(Usuario, user.id))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_tipo_archivo_invalido(db_session):
    """Rechaza un tipo de archivo fuera del CHECK."""
    user = make_usuario()
    espacio = make_espacio(user.id)
    with pytest.raises(IntegrityError):
        make_archivo(user.id, espacio.id, tipo="borrador")
