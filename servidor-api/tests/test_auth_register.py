"""Pruebas de registro de usuarios."""

from sqlalchemy import func, select

from app.audit.models import Auditoria
from app.extensions import db
from app.users.models import Usuario
from app.workspaces.models import EspacioTrabajo, MembresiaEspacio
from tests.auth_helpers import register


def test_register_creates_user_workspace_membership_audit(auth_client, app):
    """Registro correcto crea usuario, espacio, membresía y auditoría."""
    response = register(auth_client)
    assert response.status_code == 201
    body = response.get_json()["user"]
    assert body["correo"] == "ana@example.com"
    assert body["rol_global"] == "usuario"
    assert "password_hash" not in body
    with app.app_context():
        user = db.session.scalars(select(Usuario)).one()
        assert user.password_hash != "password12345"
        assert "password12345" not in user.password_hash
        espacio = db.session.scalars(select(EspacioTrabajo)).one()
        assert espacio.tipo == "individual"
        assert espacio.nombre == "Espacio de Ana"
        memb = db.session.scalars(select(MembresiaEspacio)).one()
        assert memb.rol == "propietario" and memb.tipo_espacio == "individual"
        actions = db.session.scalars(select(Auditoria.accion)).all()
        assert "usuario_registrado" in actions


def test_register_duplicate_email_case_insensitive(auth_client, app):
    """Correo repetido con otra capitalización responde 409."""
    assert register(auth_client, correo="Ana@Example.com").status_code == 201
    response = register(auth_client, correo="ana@example.com", nombre="Otra")
    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "email_taken"


def test_register_validation_errors(auth_client, app):
    """Contraseña corta, correo inválido o nombre vacío → 400 por campo."""
    response = register(auth_client, nombre="", correo="malo", password="corta")
    assert response.status_code == 400
    fields = response.get_json()["error"]["fields"]
    assert "nombre" in fields and "correo" in fields and "contraseña" in fields


def test_register_rejects_role_field(auth_client, app):
    """rol_global en registro → 400 validation_error y no crea usuario."""
    response = register(auth_client, rol_global="admin_general", estado="activo", id="x")
    assert response.status_code == 400
    body = response.get_json()["error"]
    assert body["code"] == "validation_error"
    assert body["fields"]["rol_global"] == "Campo no permitido."
    with app.app_context():
        assert db.session.scalar(select(func.count()).select_from(Usuario)) == 0
