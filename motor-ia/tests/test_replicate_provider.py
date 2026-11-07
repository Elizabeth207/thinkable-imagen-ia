"""Pruebas del proveedor con dobles de prueba. No hay red ni cobro."""

import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
import httpx
import pytest
from PIL import Image
from motor_ia.errors import JobFailedError, JobTimeoutError, MotorIAError, ProviderUnavailableError
from motor_ia.models import EnhanceOptions, JobState, JobStatus
from motor_ia.providers.base import ImageProvider
from motor_ia.providers.replicate_provider import ReplicateImageProvider, describe_preset

_TOKEN = "test-token"
_OPTIONS = EnhanceOptions("gfpgan", 0.5, 30)

def test_submit_creates_one_prediction(tmp_path: Path) -> None:
    """Un envío llama a create una sola vez, con la versión verificada."""
    client, path = MagicMock(), tmp_path / "face.png"
    Image.new("RGB", (8, 8), "white").save(path, format="PNG")

    def _create(**kwargs):
        assert kwargs["input"]["img"].closed is False and kwargs["wait"] is False
        assert kwargs["version"].startswith("tencentarc/gfpgan:0fbacf7a")
        assert kwargs["input"]["version"] == "v1.4"
        return SimpleNamespace(id="job-1")

    client.predictions.create.side_effect = _create
    provider = ReplicateImageProvider(_TOKEN, client=client)
    assert provider.submit(path, _OPTIONS) == "job-1"
    assert client.predictions.create.call_count == 1 and _TOKEN not in repr(provider)
    assert "xinntao/realesrgan:1b976a4d" in describe_preset("realesrgan")

@pytest.mark.parametrize(("remote", "local"), [("starting", JobState.PENDING), ("processing", JobState.PROCESSING), ("succeeded", JobState.COMPLETED), ("failed", JobState.FAILED), ("canceled", JobState.FAILED)])
def test_status_mapping(remote: str, local: JobState) -> None:
    """Los cinco estados documentados se normalizan sin crear otro trabajo."""
    client = MagicMock()
    client.predictions.get.return_value = SimpleNamespace(status=remote, error="boom")
    status = ReplicateImageProvider(_TOKEN, client=client).get_status("job-9")
    assert status.state is local and client.predictions.create.call_count == 0

def test_unknown_status_and_preset_do_not_call_create() -> None:
    """Un estado o un preset no verificados no crean una predicción."""
    client = MagicMock()
    client.predictions.get.return_value = SimpleNamespace(status="queued", error=None)
    provider = ReplicateImageProvider(_TOKEN, client=client)
    with pytest.raises(ProviderUnavailableError, match="no documentado"):
        provider.get_status("job-9")
    with pytest.raises(MotorIAError, match="desconocido"):
        provider.submit(Path("unused.png"), EnhanceOptions("inventado", 0.5, 30))
    assert client.predictions.create.call_count == 0

def test_result_downloads_https_output_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """La URI https documentada se descarga y el token no queda en la etiqueta."""
    client = MagicMock()
    client.predictions.get.return_value = SimpleNamespace(
        status="succeeded", error=None, model="tencentarc/gfpgan", version="0fbacf7a",
        output="https://replicate.delivery/example/output.png",
    )

    def _get(url: str, headers: dict[str, str], timeout: float) -> httpx.Response:
        assert headers["Authorization"] == f"Bearer {_TOKEN}"
        return httpx.Response(200, content=b"png-bytes", request=httpx.Request("GET", url))

    monkeypatch.setattr("motor_ia.providers.replicate_provider.httpx.get", _get)
    result = ReplicateImageProvider(_TOKEN, client=client).get_result("job-2")
    assert result.output_bytes == b"png-bytes" and client.predictions.create.call_count == 0
    assert _TOKEN not in result.model_label

def test_failed_result_does_not_resubmit() -> None:
    """Un trabajo fallido se informa y no se vuelve a crear."""
    client = MagicMock()
    client.predictions.get.return_value = SimpleNamespace(status="failed", error="gpu", output=None)
    with pytest.raises(JobFailedError, match="gpu"):
        ReplicateImageProvider(_TOKEN, client=client).get_result("job-3")
    assert client.predictions.create.call_count == 0

def test_timeout_does_not_resubmit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Agotar el tiempo no llama a submit."""
    monkeypatch.setattr(time, "sleep", lambda _seconds: None)
    provider = _Pending()
    with pytest.raises(JobTimeoutError, match="no se reenvió"):
        provider.wait_for_completion("job", EnhanceOptions("gfpgan", 0.1, 0))
    assert provider.submits == 0

class _Pending(ImageProvider):
    """Proveedor que se queda en espera, para probar el sondeo."""

    submits = 0
    def submit(self, image_path: Path, options: EnhanceOptions) -> str:
        self.submits += 1
        return "job"

    def get_status(self, job_id: str) -> JobStatus:
        return JobStatus(job_id, JobState.PENDING, None)

    def get_result(self, job_id: str):
        raise AssertionError("no debe descargar")
