"""Sin datos sensibles en logs ni en auditoría."""

import logging

from sqlalchemy import select

from app.audit.models import Auditoria
from app.extensions import db
from tests.auth_helpers import csrf_headers, login, register


def test_password_not_in_logs_or_audit(auth_client, app, caplog):
    """Contraseña reconocible no aparece en logs ni en filas de auditoría."""
    secret = "UniqueSecret99"
    with caplog.at_level(logging.DEBUG):
        assert register(auth_client, password=secret).status_code == 201
        auth_client.get("/api/auth/me")
        auth_client.post("/api/auth/logout", headers=csrf_headers(auth_client))
        assert login(auth_client, password=secret).status_code == 200
    joined = " ".join(record.getMessage() for record in caplog.records)
    assert secret not in joined
    with app.app_context():
        for row in db.session.scalars(select(Auditoria)).all():
            blob = f"{row.accion}{row.tipo_objetivo}{row.usuario_id}{row.objetivo_id}"
            assert secret not in blob
            assert "csrf" not in row.accion.lower()
