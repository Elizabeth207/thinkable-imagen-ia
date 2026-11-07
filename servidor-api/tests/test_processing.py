"""Restricciones de proveedores_ia y procesamientos_ia."""

import pytest
from sqlalchemy.exc import IntegrityError

from tests.builders import (
    make_archivo,
    make_espacio,
    make_procesamiento,
    make_proveedor,
    make_usuario,
)


def test_proveedor_y_procesamiento_validos(db_session):
    """Acepta proveedor y un procesamiento pendiente."""
    user = make_usuario()
    espacio = make_espacio(user.id)
    original = make_archivo(user.id, espacio.id)
    proveedor = make_proveedor()
    job = make_procesamiento(
        user.id,
        espacio.id,
        original.id,
        proveedor_id=proveedor.id,
    )
    db_session.commit()
    assert job.estado == "pendiente"


def test_completado_exige_resultado(db_session):
    """Un procesamiento completado debe tener archivo_resultado_id."""
    user = make_usuario()
    espacio = make_espacio(user.id)
    original = make_archivo(user.id, espacio.id)
    with pytest.raises(IntegrityError):
        make_procesamiento(
            user.id,
            espacio.id,
            original.id,
            estado="completado",
            archivo_resultado_id=None,
        )


def test_estado_procesamiento_invalido(db_session):
    """Rechaza un estado de procesamiento fuera del CHECK."""
    user = make_usuario()
    espacio = make_espacio(user.id)
    original = make_archivo(user.id, espacio.id)
    with pytest.raises(IntegrityError):
        make_procesamiento(user.id, espacio.id, original.id, estado="pausado")
