"""Restricciones de espacios_trabajo y membresias_espacio."""

import pytest
from sqlalchemy.exc import IntegrityError

from tests.builders import make_espacio, make_membresia, make_usuario


def test_espacio_y_membresia_validos(db_session):
    """Acepta un espacio individual con su membresía."""
    user = make_usuario()
    espacio = make_espacio(user.id)
    memb = make_membresia(user.id, espacio.id, "individual")
    db_session.commit()
    assert espacio.tipo == "individual"
    assert memb.rol == "propietario"


def test_un_solo_espacio_individual(db_session):
    """Un usuario no puede tener dos espacios individuales."""
    user = make_usuario()
    make_espacio(user.id, nombre="Uno")
    db_session.commit()
    with pytest.raises(IntegrityError):
        make_espacio(user.id, nombre="Dos")


def test_un_solo_equipo_grupal(db_session):
    """Un usuario pertenece como máximo a un equipo grupal."""
    owner = make_usuario(correo="a@ex.com")
    other = make_usuario(nombre="B", correo="b@ex.com")
    g1 = make_espacio(owner.id, nombre="T1", tipo="grupal")
    g2 = make_espacio(other.id, nombre="T2", tipo="grupal")
    make_membresia(owner.id, g1.id, "grupal")
    db_session.commit()
    with pytest.raises(IntegrityError):
        make_membresia(owner.id, g2.id, "grupal", rol="participante")


def test_tipo_espacio_debe_coincidir(db_session):
    """La FK compuesta rechaza un tipo_espacio incorrecto."""
    user = make_usuario()
    espacio = make_espacio(user.id, tipo="individual")
    db_session.commit()
    with pytest.raises(IntegrityError):
        make_membresia(user.id, espacio.id, "grupal")


def test_rol_membresia_invalido(db_session):
    """Rechaza un rol de membresía fuera del CHECK."""
    user = make_usuario()
    espacio = make_espacio(user.id)
    with pytest.raises(IntegrityError):
        make_membresia(user.id, espacio.id, "individual", rol="viewer")
