"""CSV de la prueba y guardado de la imagen resultante."""

import csv
import io
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError


@dataclass(frozen=True)
class ResultRow:
    """Una fila del informe de la prueba real."""

    nombre_archivo: str
    modelo_version: str
    estado: str
    segundos: float
    resolucion_original: str
    resolucion_resultado: str
    tamano_kb: float | str
    mensaje_error: str


def write_results(path: Path, rows: list[ResultRow]) -> None:
    """Guarda el CSV en UTF-8 con BOM para que Excel lo abra bien."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(ResultRow.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def save_result(folder: Path, source: Path, data: bytes) -> tuple[str, float]:
    """Guarda los bytes y devuelve la resolución y el tamaño en KB."""
    folder.mkdir(parents=True, exist_ok=True)
    resolution, extension = _measure(data)
    (folder / f"{source.stem}-result{extension}").write_bytes(data)
    return resolution, round(len(data) / 1024, 1)


def _measure(data: bytes) -> tuple[str, str]:
    try:
        with Image.open(io.BytesIO(data)) as image:
            extension = {"JPEG": ".jpg", "PNG": ".png"}.get(image.format or "", ".bin")
            return f"{image.size[0]}x{image.size[1]}", extension
    except (UnidentifiedImageError, OSError):
        return "", ".bin"
