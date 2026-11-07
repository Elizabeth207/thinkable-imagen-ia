"""Datos del trabajo de mejora. No conocen a ningún proveedor."""

from dataclasses import dataclass
from enum import Enum


class JobState(str, Enum):
    """Estados normalizados, independientes del proveedor."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class EnhanceOptions:
    """Opciones locales de un trabajo de mejora."""

    preset: str
    poll_interval_seconds: float
    max_wait_seconds: float


@dataclass(frozen=True)
class JobStatus:
    """Estado consultado de un trabajo ya enviado."""

    job_id: str
    state: JobState
    error_message: str | None


@dataclass(frozen=True)
class JobResult:
    """Resultado descargado cuando el trabajo terminó bien."""

    job_id: str
    state: JobState
    output_bytes: bytes
    error_message: str | None
    model_label: str
