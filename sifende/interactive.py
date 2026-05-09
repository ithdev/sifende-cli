"""Guided builder for electronic document payloads — pure `input()`."""

from __future__ import annotations

from datetime import datetime
from typing import List

from .errors import ValidationError
from .utils.formatting import fmt_pyg
from .utils.io import prompt
from .utils.validation import validate_pyg


_TIPO_DOC_CHOICES = {
    "1": "FACTURA_ELECTRONICA",
    "2": "NOTA_DE_CREDITO_ELECTRONICA",
    "3": "NOTA_DE_DEBITO_ELECTRONICA",
}
_MONEDA_CHOICES = {"1": "PYG", "2": "USD", "3": "BRL", "4": "ARS", "5": "EUR"}
_OP_CHOICES = {"1": "B2C", "2": "B2B", "3": "B2G"}
_IVA_CHOICES = {
    "1": (10, "GRAVADO"),
    "2": (5, "GRAVADO"),
    "3": (0, "EXENTO"),
    "4": (0, "EXONERADO"),
}
_TIPO_DOC_RECEPTOR_CHOICES = {
    "1": "CEDULA_PARAGUAYA",
    "2": "PASAPORTE",
    "3": "CEDULA_EXTRANJERA",
    "4": "CARNET_DE_RESIDENCIA",
    "5": "TARJETA_DIPLOMATICA",
    "6": "OTRO",
}
_TIPO_PAGO_CHOICES = {
    "1": "EFECTIVO",
    "2": "TARJETA_CREDITO",
    "3": "TARJETA_DEBITO",
    "4": "TRANSFERENCIA",
    "5": "CHEQUE",
    "6": "BILLETERA_VIRTUAL",
    "7": "OTRO",
}


def _choice(value: str, mapping: dict, *, field: str) -> str:
    if value not in mapping:
        raise ValidationError(field, f"opción inválida: {value!r}")
    return value


def _int_validator(field: str):
    def _v(s: str) -> str:
        try:
            n = int(s)
        except ValueError:
            raise ValidationError(field, "se esperaba un entero")
        validate_pyg(n, field=field)
        return str(n)
    return _v


def _yesno(value: str) -> str:
    v = value.strip().lower()
    if v in ("s", "si", "sí", "y", "yes"):
        return "s"
    if v in ("n", "no"):
        return "n"
    raise ValidationError("respuesta", "responda 's' o 'n'")


def build_factura_interactive() -> dict:
    """Run the interactive wizard. Raises KeyboardInterrupt on Ctrl+C."""
    print("=== Sifende — Nuevo Documento Electrónico ===")

    tipo_key = prompt(
        "Tipo de documento: 1) FACTURA  2) NOTA_CREDITO  3) NOTA_DEBITO",
        default="1",
        validator=lambda s: _choice(s, _TIPO_DOC_CHOICES, field="tipoDocumento"),
    )
    tipo_doc = _TIPO_DOC_CHOICES[tipo_key]

    establecimiento = int(prompt("Nro. establecimiento (entero, ej: 1)", default="1", validator=_int_validator("numeroEstablecimiento")))
    punto_exp = int(prompt("Punto de expedición (entero, ej: 1)", default="1", validator=_int_validator("puntoExpedicion")))

    fecha_default = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    fecha = prompt("Fecha de emisión (YYYY-MM-DDTHH:mm:ss)", default=fecha_default)

    moneda_key = prompt(
        "Moneda: 1)PYG  2)USD  3)BRL  4)ARS  5)EUR",
        default="1",
        validator=lambda s: _choice(s, _MONEDA_CHOICES, field="monedaOperacion"),
    )
    moneda = _MONEDA_CHOICES[moneda_key]

    op_key = prompt(
        "Tipo de operación: 1)B2C  2)B2B  3)B2G",
        default="1",
        validator=lambda s: _choice(s, _OP_CHOICES, field="tipoOperacion"),
    )
    tipo_op = _OP_CHOICES[op_key]

    print("\n— Receptor —")
    if tipo_op in ("B2B", "B2G"):
        receptor_ruc = prompt("RUC del receptor (numero-dv)")
        receptor: dict = {
            "tipoContribuyente": "CONTRIBUYENTE",
            "tipoOperacion": tipo_op,
            "tipoDocumento": "RUC",
            "numeroDocumento": receptor_ruc,
            "nombreRazonSocial": prompt("Razón social del receptor"),
        }
    else:
        doc_key = prompt(
            "Tipo doc receptor: 1)Cédula PY  2)Pasaporte  3)Cédula Ext  4)Carnet Res  5)T.Diplomática  6)Otro",
            default="1",
            validator=lambda s: _choice(s, _TIPO_DOC_RECEPTOR_CHOICES, field="tipoDocumento"),
        )
        receptor = {
            "tipoContribuyente": "NO_CONTRIBUYENTE",
            "tipoOperacion": "B2C",
            "tipoDocumento": _TIPO_DOC_RECEPTOR_CHOICES[doc_key],
            "numeroDocumento": prompt("Número de documento del receptor"),
            "nombreRazonSocial": prompt("Nombre del receptor"),
        }

    print("\n— Ítems —")
    items: List[dict] = []
    while True:
        prefix = "Agregar otro ítem (s/n)" if items else "Agregar ítem (s/n)"
        default = "n" if items else "s"
        if prompt(prefix, default=default, validator=_yesno) == "n":
            if items:
                break
            print("  ! debe haber al menos un ítem")
            continue

        descripcion = prompt("  Descripción")
        cantidad = int(prompt("  Cantidad", default="1", validator=_int_validator("cantidad")))
        precio_unit = int(prompt("  Precio unitario (entero)", validator=_int_validator("precioUnitario")))
        iva_key = prompt(
            "  IVA: 1)10%  2)5%  3)Exento  4)Exonerado",
            default="1",
            validator=lambda s: _choice(s, _IVA_CHOICES, field="tasaIVA"),
        )
        tasa_iva, afectacion = _IVA_CHOICES[iva_key]

        items.append({
            "codigo": f"ITEM-{len(items) + 1:03d}",
            "descripcion": descripcion,
            "unidadMedida": "UNI",
            "cantidad": cantidad,
            "precioUnitario": precio_unit,
            "tasaIVA": tasa_iva,
            "afectacionTributaria": afectacion,
        })

    print("\n— Pago —")
    pago_key = prompt(
        "Tipo de pago: 1)Efectivo  2)T.Crédito  3)T.Débito  4)Transferencia  5)Cheque  6)Billetera  7)Otro",
        default="1",
        validator=lambda s: _choice(s, _TIPO_PAGO_CHOICES, field="tipoPago"),
    )
    total_general = sum(i["precioUnitario"] * i["cantidad"] for i in items)
    condicion_pago = {
        "tipo": "CONTADO",
        "tipoPago": _TIPO_PAGO_CHOICES[pago_key],
        "monedaPago": moneda,
        "montoPago": total_general,
    }

    print(f"\nResumen: {len(items)} ítem(s) — Total: {fmt_pyg(total_general)} {moneda}")
    confirm = prompt("Confirmar emisión (s/n)", default="s", validator=_yesno)
    if confirm != "s":
        raise KeyboardInterrupt

    return {
        "tipoDocumento": tipo_doc,
        "tipoEmision": "NORMAL",
        "tipoTransaccion": "VENTA_MERCADERIA",
        "fechaEmision": fecha,
        "numeroEstablecimiento": establecimiento,
        "puntoExpedicion": punto_exp,
        "monedaOperacion": moneda,
        "condicionOperacion": "CONTADO",
        "condicionPago": condicion_pago,
        "receptor": receptor,
        "items": items,
    }
