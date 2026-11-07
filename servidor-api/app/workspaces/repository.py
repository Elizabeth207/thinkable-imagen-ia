"""Creación y consulta de espacios de trabajo."""

from uuid import UUID

from sqlalchemy import select

from app.extensions import db
from app.workspaces.models import EspacioTrabajo, MembresiaEspacio


def find_individual_workspace(user_id: UUID) -> EspacioTrabajo | None:
    """Devuelve el espacio individual del usuario, si existe."""
    stmt = select(EspacioTrabajo).where(
        EspacioTrabajo.propietario_id == user_id,
        EspacioTrabajo.tipo == "individual",
    )
    return db.session.scalars(stmt).first()


def create_individual_workspace(user_id: UUID, owner_name: str) -> EspacioTrabajo:
    """Crea el espacio personal y la membresía de propietario."""
    espacio = EspacioTrabajo(
        propietario_id=user_id,
        nombre=f"Espacio de {owner_name}",
        tipo="individual",
        estado="activo",
    )
    db.session.add(espacio)
    db.session.flush()
    membresia = MembresiaEspacio(
        usuario_id=user_id,
        espacio_id=espacio.id,
        tipo_espacio="individual",
        rol="propietario",
    )
    db.session.add(membresia)
    db.session.flush()
    return espacio
