"""Pruebas del comando flask create-admin."""

from sqlalchemy import select

from app.users.models import Usuario
from app.workspaces.models import EspacioTrabajo, MembresiaEspacio
from tests.auth_helpers import register


def test_create_admin_success_and_duplicate(app, db_session):
    """create-admin crea el administrador y rechaza correo repetido."""
    runner = app.test_cli_runner()
    first = runner.invoke(
        args=["create-admin"],
        input="admin@example.com\nAdmin\npassword12345\npassword12345\n",
    )
    assert first.exit_code == 0
    assert "Administrador creado" in first.output
    user = db_session.scalars(select(Usuario)).one()
    assert user.rol_global == "admin_general"
    assert "password12345" not in user.password_hash
    assert db_session.scalars(select(EspacioTrabajo)).one().tipo == "individual"
    assert db_session.scalars(select(MembresiaEspacio)).one().rol == "propietario"
    second = runner.invoke(
        args=["create-admin"],
        input="admin@example.com\nOtro\npassword12345\npassword12345\n",
    )
    assert second.exit_code != 0
    assert "ya está registrado" in second.output


def test_create_admin_rejects_existing_register_email(app, auth_client):
    """Si el correo ya existe por registro, create-admin falla."""
    register(auth_client, correo="dup@example.com")
    runner = app.test_cli_runner()
    result = runner.invoke(
        args=["create-admin"],
        input="dup@example.com\nAdmin\npassword12345\npassword12345\n",
    )
    assert result.exit_code != 0
    assert "ya está registrado" in result.output
