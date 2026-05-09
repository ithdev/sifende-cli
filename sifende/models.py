"""Domain models: states + typed response dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


class Estado:
    """SIFEN document lifecycle states.

    Modeled as plain strings (not enum.Enum) so the wire format and the
    printed form stay identical and JSON serialization is trivial.
    """

    PENDIENTE = "PENDIENTE"
    EN_LOTE = "EN_LOTE"
    ENVIADO = "ENVIADO"
    APROBADO = "APROBADO"
    APROBADO_OBSERVACION = "APROBADO_OBSERVACION"
    RECHAZADO = "RECHAZADO"
    ERROR = "ERROR"
    CANCELADO = "CANCELADO"


TERMINAL_ESTADOS = frozenset({
    Estado.APROBADO,
    Estado.APROBADO_OBSERVACION,
    Estado.RECHAZADO,
    Estado.ERROR,
    Estado.CANCELADO,
})
SUCCESS_ESTADOS = frozenset({Estado.APROBADO})


@dataclass(frozen=True)
class EmitirResponse:
    cdc: str
    estado: str
    id: Optional[str] = None
    status_url: Optional[str] = None
    kude_url: Optional[str] = None
    qr_url: Optional[str] = None
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_api(cls, payload: dict) -> "EmitirResponse":
        return cls(
            cdc=str(payload.get("cdc", "")),
            estado=str(payload.get("estado", Estado.PENDIENTE)),
            id=_opt_str(payload.get("id")),
            status_url=_opt_str(payload.get("statusUrl")),
            kude_url=_opt_str(payload.get("kudeUrl")),
            qr_url=_opt_str(payload.get("qrUrl")),
            raw=payload,
        )

    def to_dict(self) -> dict:
        return {
            "cdc": self.cdc,
            "estado": self.estado,
            "id": self.id,
            "statusUrl": self.status_url,
            "kudeUrl": self.kude_url,
            "qrUrl": self.qr_url,
        }


@dataclass(frozen=True)
class EstadoResponse:
    cdc: str
    estado: str
    mensaje_rechazo: Optional[str] = None
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_api(cls, payload: dict) -> "EstadoResponse":
        return cls(
            cdc=str(payload.get("cdc", "")),
            estado=str(payload.get("estado", "")),
            mensaje_rechazo=_opt_str(payload.get("mensajeRechazo")),
            raw=payload,
        )

    def to_dict(self) -> dict:
        return {
            "cdc": self.cdc,
            "estado": self.estado,
            "mensajeRechazo": self.mensaje_rechazo,
        }

    @property
    def is_terminal(self) -> bool:
        return self.estado in TERMINAL_ESTADOS

    @property
    def is_success(self) -> bool:
        return self.estado in SUCCESS_ESTADOS


def _opt_str(v: Any) -> Optional[str]:
    if v is None:
        return None
    s = str(v)
    return s if s else None
