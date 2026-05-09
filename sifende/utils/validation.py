"""Local validators — fail fast before hitting the network."""

from __future__ import annotations

import re
from datetime import datetime

from ..errors import ValidationError


_RUC_RE = re.compile(r"^\d{1,8}-\d$")
_CDC_RE = re.compile(r"^\d{44}$")


def validate_ruc(value: str, *, field: str = "ruc") -> str:
    if not isinstance(value, str) or not _RUC_RE.match(value):
        raise ValidationError(field, f"formato RUC inválido (esperado 'numero-dv'): {value!r}")
    return value


def validate_cdc(value: str, *, field: str = "cdc") -> str:
    if not isinstance(value, str) or not _CDC_RE.match(value):
        raise ValidationError(field, f"el CDC debe ser de 44 dígitos: {value!r}")
    return value


def validate_iso_no_tz(value: str, *, field: str = "fechaEmision") -> str:
    if not isinstance(value, str):
        raise ValidationError(field, "se esperaba string YYYY-MM-DDTHH:mm:ss")
    if value.endswith("Z") or "+" in value[10:] or value.count("-") > 2:
        raise ValidationError(field, "no debe incluir zona horaria (sin Z ni offset)")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise ValidationError(field, f"formato de fecha inválido: {value!r}")
    return value


def validate_pyg(value, *, field: str = "monto") -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(field, "los montos en PYG deben ser enteros")
    if value < 0:
        raise ValidationError(field, "los montos no pueden ser negativos")
    return value


def validate_motivo(value: str, *, field: str = "motivo", min_len: int = 5) -> str:
    if not isinstance(value, str) or len(value.strip()) < min_len:
        raise ValidationError(field, f"el motivo debe tener al menos {min_len} caracteres")
    return value.strip()


def validate_factura_payload(payload: dict) -> dict:
    """Defense-in-depth check before posting. SIFEN is the source of truth;
    this only catches obvious shape errors that would make the call wasted.
    """
    if not isinstance(payload, dict):
        raise ValidationError("payload", "se esperaba un objeto JSON")

    required = (
        "tipoDocumento",
        "tipoEmision",
        "fechaEmision",
        "numeroEstablecimiento",
        "puntoExpedicion",
        "monedaOperacion",
        "receptor",
        "condicionOperacion",
        "items",
    )
    missing = [k for k in required if k not in payload]
    if missing:
        raise ValidationError("payload", f"campos requeridos ausentes: {', '.join(missing)}")

    validate_iso_no_tz(payload["fechaEmision"], field="fechaEmision")

    items = payload["items"]
    if not isinstance(items, list) or not items:
        raise ValidationError("items", "debe haber al menos un ítem")
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValidationError(f"items[{i}]", "se esperaba un objeto")
        for k in ("descripcion", "cantidad", "precioUnitario", "tasaIVA", "afectacionTributaria"):
            if k not in item:
                raise ValidationError(f"items[{i}].{k}", "campo requerido")
        validate_pyg(item["precioUnitario"], field=f"items[{i}].precioUnitario")

    receptor = payload["receptor"]
    if not isinstance(receptor, dict):
        raise ValidationError("receptor", "se esperaba un objeto")
    for k in ("tipoContribuyente", "tipoOperacion", "nombreRazonSocial"):
        if k not in receptor:
            raise ValidationError(f"receptor.{k}", "campo requerido")

    return payload
