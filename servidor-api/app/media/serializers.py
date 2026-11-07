"""Serialización pública de archivos multimedia."""

from app.media.models import ArchivoMultimedia


def serialize_archivo(row: ArchivoMultimedia) -> dict:
    """Metadatos seguros para el cliente (sin rutas internas sensibles extra)."""
    return {
        "id": str(row.id),
        "nombre_original": row.nombre_original,
        "tipo": row.tipo,
        "mime_type": row.mime_type,
        "tamano_bytes": row.tamano_bytes,
        "ancho": row.ancho,
        "alto": row.alto,
        "checksum_sha256": row.checksum_sha256,
        "creado_en": row.creado_en.isoformat(),
    }
