"""Prueba real con las imágenes de samples/. No simula al proveedor ni genera fotos."""

import argparse
import time
from pathlib import Path
from dotenv import load_dotenv
from motor_ia.config import load_settings
from motor_ia.errors import JobFailedError, JobTimeoutError, MotorIAError
from motor_ia.models import EnhanceOptions
from motor_ia.providers.replicate_provider import ReplicateImageProvider, describe_preset
from motor_ia.validation.image_checks import inspect_image
from report_writer import ResultRow, save_result, write_results

_ROOT = Path(__file__).resolve().parents[2]
_BASE = Path(__file__).resolve().parents[1]
_SAMPLES, _OUTPUT, _DEFAULT_MAX = _BASE / "samples", _BASE / "out", 3

def main(argv: list[str] | None = None) -> int:
    """Procesa hasta el tope indicado y escribe out/resultados.csv."""
    parser = argparse.ArgumentParser(description="Prueba real de mejora de imágenes.")
    parser.add_argument("--max-images", type=int, default=_DEFAULT_MAX)
    parser.add_argument("--preset", default=None)
    args = parser.parse_args(argv)
    planned = _select(args.max_images)
    if planned is None:
        return 1
    ready = _open_provider(args.preset)
    if ready is None:
        return 1
    provider, options = ready
    rows = [_process(path, provider, options) for path in planned]
    write_results(_OUTPUT / "resultados.csv", rows)
    print(f"Listo. Filas: {len(rows)}. CSV: {_OUTPUT / 'resultados.csv'}")
    return 0

def _select(limit: int) -> list[Path] | None:
    if limit < 1:
        print("--max-images debe ser al menos 1.")
        return None
    images = _images()
    if not images:
        print("samples/ está vacío. Agrega imágenes de prueba. No se generó ni descargó ninguna.")
        return None
    planned = images[:limit]
    print(f"Se enviarán {len(planned)} imagen(es) a Replicate. Cada ejecución se cobra.")
    if len(planned) <= _DEFAULT_MAX or _accepted():
        return planned
    print("Cancelado. No se envió ninguna imagen.")
    return None

def _images() -> list[Path]:
    if not _SAMPLES.is_dir():
        return []
    files = [item for item in _SAMPLES.iterdir() if item.is_file() and item.name != ".gitkeep"]
    return sorted(files, key=lambda item: item.name)

def _accepted() -> bool:
    print(f"Eso supera el tope por defecto de {_DEFAULT_MAX} imágenes.")
    try:
        return input("Escribe SI para continuar: ").strip() == "SI"
    except EOFError:
        return False

def _open_provider(preset: str | None) -> tuple[ReplicateImageProvider, EnhanceOptions] | None:
    load_dotenv(_ROOT / ".env")
    try:
        settings = load_settings(preset)
        describe_preset(settings.preset)
    except MotorIAError as exc:
        print(exc)
        return None
    return ReplicateImageProvider(settings.api_token, settings.base_url), settings.to_options()

def _process(path: Path, provider: ReplicateImageProvider, options: EnhanceOptions) -> ResultRow:
    label = describe_preset(options.preset)
    try:
        info = inspect_image(path)
    except MotorIAError as exc:
        size = round(path.stat().st_size / 1024, 1) if path.is_file() else 0.0
        return ResultRow(path.name, label, "failed", 0, "", "", size, str(exc))
    started = time.perf_counter()
    try:
        result = _run(path, provider, options)
    except (JobFailedError, JobTimeoutError, MotorIAError) as exc:
        state = "timeout" if isinstance(exc, JobTimeoutError) else "failed"
        seconds = round(time.perf_counter() - started, 3)
        return ResultRow(path.name, label, state, seconds, info.resolution, "", info.size_kb, str(exc))
    resolution, size_kb = save_result(_OUTPUT, path, result.output_bytes)
    seconds = round(time.perf_counter() - started, 3)
    return ResultRow(path.name, result.model_label, "completed", seconds, info.resolution, resolution, size_kb, "")

def _run(path: Path, provider: ReplicateImageProvider, options: EnhanceOptions):
    job_id = provider.submit(path, options)
    status = provider.wait_for_completion(job_id, options)
    if status.state.value != "completed":
        raise JobFailedError(status.error_message or "El trabajo falló. No se reenvió.")
    return provider.get_result(job_id)

if __name__ == "__main__":
    raise SystemExit(main())
