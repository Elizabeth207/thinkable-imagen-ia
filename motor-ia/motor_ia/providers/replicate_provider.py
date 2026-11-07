"""Cliente real de Replicate. Ningún detalle de esta API sale de este archivo."""

from pathlib import Path
import httpx
from replicate.client import Client
from replicate.exceptions import ReplicateError

from motor_ia.errors import JobFailedError, MotorIAError, ProviderUnavailableError
from motor_ia.models import EnhanceOptions, JobResult, JobState, JobStatus
from motor_ia.providers.base import ImageProvider

_STATUS = {"starting": JobState.PENDING, "processing": JobState.PROCESSING, "succeeded": JobState.COMPLETED, "failed": JobState.FAILED, "canceled": JobState.FAILED}
_GFPGAN = "tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c"
_ESRGAN = "xinntao/realesrgan:1b976a4d456ed9e4d1a846597b7614e79eadad3032e9124fa63859db0fd59b56"
_PRESETS = {
    "gfpgan": ("img", _GFPGAN, {"version": "v1.4", "scale": 2}),
    "realesrgan": ("img", _ESRGAN, {"version": "General - v3", "scale": 2, "face_enhance": False, "tile": 0}),
}
class ReplicateImageProvider(ImageProvider):
    def __init__(self, api_token: str, base_url: str | None = None, client: Client | None = None) -> None:
        self._token = api_token
        self._sent: dict[str, str] = {}
        extra = {"base_url": base_url} if base_url else {}
        self._client = client or Client(api_token=api_token, **extra)

    def __repr__(self) -> str:
        return "ReplicateImageProvider(api_token='***')"

    def submit(self, image_path: Path, options: EnhanceOptions) -> str:
        """Crea una predicción. Si falla, no se crea otra."""
        field, ref, params = _require(options.preset)
        payload = dict(params)
        try:
            with image_path.open("rb") as image_file:
                payload[field] = image_file
                created = self._client.predictions.create(version=ref, input=payload, wait=False)
        except (ReplicateError, httpx.HTTPError) as exc:
            raise ProviderUnavailableError("El proveedor no respondió al crear el trabajo.") from exc
        self._sent[created.id] = options.preset
        return created.id

    def get_status(self, job_id: str) -> JobStatus:
        """Traduce el estado documentado de la predicción."""
        prediction = _fetch(self, job_id)
        return JobStatus(job_id, _state(prediction.status), _failure(prediction.status, prediction.error))

    def get_result(self, job_id: str) -> JobResult:
        """Descarga la salida. No crea otra predicción."""
        prediction = _fetch(self, job_id)
        state = _state(prediction.status)
        if state is JobState.FAILED:
            raise JobFailedError(_failure(prediction.status, prediction.error) or "El trabajo falló.")
        if state is not JobState.COMPLETED:
            raise MotorIAError("El trabajo todavía no termina. No se descargó la salida.")
        suffix = f" | {describe_preset(self._sent[job_id])}" if job_id in self._sent else ""
        label = f"{prediction.model}:{prediction.version}{suffix}"
        return JobResult(job_id, state, _output_bytes(prediction.output, self._token), None, label)

def describe_preset(preset: str) -> str:
    """Modelo, versión y parámetros verificados, sin llamar a la red."""
    _field, ref, params = _require(preset)
    return f"{ref} params={params}"

def _require(preset: str) -> tuple[str, str, dict]:
    if preset not in _PRESETS:
        known = ", ".join(sorted(_PRESETS))
        raise MotorIAError(f"Preset desconocido: {preset}. Usables: {known}.")
    return _PRESETS[preset]

def _fetch(provider: ReplicateImageProvider, job_id: str):
    try:
        return provider._client.predictions.get(job_id)
    except (ReplicateError, httpx.HTTPError) as exc:
        raise ProviderUnavailableError("El proveedor no respondió al consultar el trabajo.") from exc

def _state(status: str) -> JobState:
    if status not in _STATUS:
        raise ProviderUnavailableError(f"Estado no documentado: {status}")
    return _STATUS[status]

def _failure(status: str, error: str | None) -> str | None:
    if status == "canceled":
        return error or "La predicción fue cancelada."
    if status == "failed":
        return error or "La predicción falló."
    return None

def _output_bytes(output: object, token: str) -> bytes:
    reader = getattr(output, "read", None)
    if callable(reader) and isinstance(data := reader(), bytes):
        return data
    if not (isinstance(output, str) and output.startswith("https://")):
        raise ProviderUnavailableError("La salida no tiene la forma documentada (URI https).")
    try:
        response = httpx.get(output, headers={"Authorization": f"Bearer {token}"}, timeout=30.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ProviderUnavailableError("No se pudo descargar la imagen resultante.") from exc
    return response.content
