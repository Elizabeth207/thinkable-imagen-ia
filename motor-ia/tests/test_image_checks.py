"""Pruebas de validación local. Usan imágenes sintéticas temporales, no samples/."""

from pathlib import Path

import pytest
from PIL import Image

from motor_ia.errors import InvalidImageError
from motor_ia.validation import image_checks
from motor_ia.validation.image_checks import inspect_image


def test_png_is_accepted(tmp_path: Path) -> None:
    """Un PNG real de Pillow se acepta y conserva sus medidas."""
    path = tmp_path / "swatch.png"
    Image.new("RGB", (4, 6), "red").save(path, format="PNG")
    info = inspect_image(path)
    assert info.resolution == "4x6"
    assert info.image_format == "PNG"
    assert info.size_kb > 0


def test_text_file_is_rejected(tmp_path: Path) -> None:
    """Un archivo que no es imagen no pasa."""
    path = tmp_path / "notes.txt"
    path.write_text("no es una imagen", encoding="utf-8")
    with pytest.raises(InvalidImageError):
        inspect_image(path)


def test_unconfirmed_format_is_rejected(tmp_path: Path) -> None:
    """BMP es imagen real, pero no aparece en los ejemplos oficiales consultados."""
    path = tmp_path / "swatch.bmp"
    Image.new("RGB", (2, 2), "blue").save(path, format="BMP")
    with pytest.raises(InvalidImageError, match="no confirmado"):
        inspect_image(path)


def test_oversized_file_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """El tope documentado de 100 MB se aplica antes de llamar al proveedor."""
    path = tmp_path / "swatch.png"
    Image.new("RGB", (2, 2), "white").save(path, format="PNG")
    monkeypatch.setattr(image_checks, "MAX_UPLOAD_BYTES", 10)
    with pytest.raises(InvalidImageError, match="100 MB"):
        inspect_image(path)
