"""Contrato del proveedor y sondeo local. No reenvía trabajos."""

import time
from abc import ABC, abstractmethod
from pathlib import Path

from motor_ia.errors import JobTimeoutError
from motor_ia.models import EnhanceOptions, JobResult, JobState, JobStatus


class ImageProvider(ABC):
    """Operaciones de un proveedor de mejora de imágenes."""

    @abstractmethod
    def submit(self, image_path: Path, options: EnhanceOptions) -> str:
        """Envía una imagen y devuelve el id del trabajo."""

    @abstractmethod
    def get_status(self, job_id: str) -> JobStatus:
        """Consulta el estado normalizado del trabajo."""

    @abstractmethod
    def get_result(self, job_id: str) -> JobResult:
        """Descarga el resultado si el trabajo ya terminó bien."""

    def wait_for_completion(self, job_id: str, options: EnhanceOptions) -> JobStatus:
        """Sondea hasta un estado final o hasta agotar el tiempo."""
        deadline = time.monotonic() + options.max_wait_seconds
        while True:
            status = self.get_status(job_id)
            if status.state in (JobState.COMPLETED, JobState.FAILED):
                return status
            if time.monotonic() >= deadline:
                raise JobTimeoutError(
                    "Se agotó el tiempo de espera. El trabajo no se reenvió."
                )
            time.sleep(options.poll_interval_seconds)
