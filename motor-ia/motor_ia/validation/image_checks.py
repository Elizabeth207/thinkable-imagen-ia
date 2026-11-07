"""Valida que el archivo sea una imagen real y de un formato visto en los ejemplos."""

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from motor_ia.errors import InvalidImageError

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
ALLOWED_FORMATS = frozenset({"JPEG", "PNG"})


@dataclass(frozen=True)
class ImageInfo:
    """Medidas locales de una imagen aceptada."""

    width: int
    height: int
    size_bytes: int
    image_format: str

    @property
    def resolution(self) -> str:
        """Resolución en ancho x alto."""
        return f"{self.width}x{self.height}"

    @property
    def size_kb(self) -> float:
        """Tamaño del archivo en KB, con un decimal."""
        return round(self.size_bytes / 1024, 1)


def inspect_image(path: Path) -> ImageInfo:
    """Rechaza lo que no sea JPEG o PNG, o supere el tope de subida documentado."""
    if not path.is_file():
        raise InvalidImageError("La ruta no es un archivo de imagen.")
    size_bytes = path.stat().st_size
    if size_bytes > MAX_UPLOAD_BYTES:
        raise InvalidImageError("La imagen supera 100 MB, tope documentado de archivo local.")
    width, height, image_format = _read_image(path)
    if image_format not in ALLOWED_FORMATS:
        raise InvalidImageError(
            f"Formato {image_format or 'desconocido'} no confirmado. Solo JPEG y PNG."
        )
    return ImageInfo(width, height, size_bytes, image_format)


def _read_image(path: Path) -> tuple[int, int, str]:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            return image.size[0], image.size[1], image.format or ""
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidImageError("Pillow no pudo leer el archivo como imagen.") from exc
