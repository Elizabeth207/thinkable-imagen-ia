"""Restricciones de la tabla auditoria."""

from tests.builders import make_auditoria, make_usuario


def test_auditoria_valida(db_session):
    """Acepta un registro de auditoría con o sin usuario."""
    user = make_usuario()
    row = make_auditoria(usuario_id=user.id, objetivo_id=user.id)
    db_session.commit()
    assert row.accion == "login"
    assert row.fecha is not None
