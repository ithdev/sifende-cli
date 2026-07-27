"""Local validators — fail fast before hitting the network."""

from __future__ import annotations

import re
from datetime import datetime

from ..errors import ValidationError


_RUC_RE = re.compile(r"^\d{1,8}-\d$")
_CDC_RE = re.compile(r"^\d{44}$")

# tipoDocumento discriminators understood by the polymorphic API endpoint.
FACTURA = "FACTURA_ELECTRONICA"
NOTA_CREDITO = "NOTA_DE_CREDITO_ELECTRONICA"
NOTA_DEBITO = "NOTA_DE_DEBITO_ELECTRONICA"
NOTAS = frozenset({NOTA_CREDITO, NOTA_DEBITO})

# Valid `motivoEmision` values (SIFEN TiMotEmi enum) for NC/ND.
VALID_MOTIVOS = frozenset({
    "DEVOLUCION_Y_AJUSTES_DE_PRECIOS",
    "DEVOLUCION",
    "DESCUENTO",
    "BONIFICACION",
    "CREDITO_INCOBRABLE",
    "RECUPERO_DE_COSTO",
    "RECUPERO_DE_GASTO",
    "AJUSTE_DE_PRECIO",
})


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


def validate_documento_asociado(asoc, *, field: str = "documentoAsociado") -> dict:
    """Validate the reference to the original DE that a NC/ND modifies.

    Mirrors the backend `DocumentoAsociadoValidator`: only ELECTRONICO is
    accepted, and it must carry a 44-digit CDC.
    """
    if not isinstance(asoc, dict):
        raise ValidationError(field, "se esperaba un objeto")
    tipo = asoc.get("tipoDocumento")
    if tipo != "ELECTRONICO":
        raise ValidationError(
            f"{field}.tipoDocumento",
            "solo se admite documento asociado ELECTRONICO",
        )
    validate_cdc(asoc.get("cdc") or "", field=f"{field}.cdc")
    return asoc


def validate_documento_payload(payload: dict) -> dict:
    """Defense-in-depth check before posting. SIFEN is the source of truth;
    this only catches obvious shape errors that would make the call wasted.

    Branches on `tipoDocumento`: FACTURA_ELECTRONICA requires
    `condicionOperacion`; NC/ND require `motivoEmision` + `documentoAsociado`.
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
        "items",
    )
    missing = [k for k in required if k not in payload]
    if missing:
        raise ValidationError("payload", f"campos requeridos ausentes: {', '.join(missing)}")

    validate_iso_no_tz(payload["fechaEmision"], field="fechaEmision")

    tipo_doc = payload["tipoDocumento"]
    if tipo_doc == FACTURA:
        if "condicionOperacion" not in payload:
            raise ValidationError("condicionOperacion", "campo requerido para factura")
    elif tipo_doc in NOTAS:
        motivo = payload.get("motivoEmision")
        if motivo is None:
            raise ValidationError("motivoEmision", "campo requerido para notas de crédito/débito")
        if motivo not in VALID_MOTIVOS:
            raise ValidationError("motivoEmision", f"motivo inválido: {motivo!r}")
        if "documentoAsociado" not in payload:
            raise ValidationError(
                "documentoAsociado", "campo requerido para notas de crédito/débito"
            )
        validate_documento_asociado(payload["documentoAsociado"])

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


# Backwards-compatible alias — the validator now covers FE + NC/ND.
validate_factura_payload = validate_documento_payload
