"""Pruebas del endpoint GET /api/health."""

from unittest.mock import patch

from sqlalchemy.exc import OperationalError


def test_health_ok_when_database_available(client):
    """Responde 200 con estado ok si la base responde."""
    with patch("app.health.service.db.session.execute") as execute:
        execute.return_value = None
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}


def test_health_503_when_database_fails(client):
    """Responde 503 JSON si SELECT 1 falla, sin detalles internos."""
    error = OperationalError("SELECT 1", {}, Exception("boom"))
    with patch("app.health.service.db.session.execute", side_effect=error):
        response = client.get("/api/health")
    body = response.get_json()
    assert response.status_code == 503
    assert body == {
        "error": {
            "code": "database_unavailable",
            "message": "La base de datos no está disponible.",
        }
    }
    assert "boom" not in str(body)
    assert "postgresql" not in str(body).lower()
