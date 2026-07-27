import builtins

import pytest

from sifende.interactive import (
    build_documento_interactive,
    build_factura_interactive,
)


def _scripted_input(monkeypatch, answers):
    it = iter(answers)

    def fake_input(_prompt=""):
        try:
            return next(it)
        except StopIteration:  # pragma: no cover - signals a wrong script
            raise AssertionError("interactive wizard asked for more input than scripted")

    monkeypatch.setattr(builtins, "input", fake_input)


# Ordered exactly as the wizard prompts (see build_documento_interactive).
_COMMON_HEAD = [
    "1",                      # establecimiento
    "1",                      # punto de expedición
    "2026-05-09T10:00:00",   # fecha
    "1",                      # moneda PYG
    "1",                      # operación B2C
    "1",                      # tipo doc receptor (cédula PY)
    "1234567",               # número documento receptor
    "JUAN PEREZ",            # nombre receptor
    "s",                      # agregar ítem
    "Devolución producto",   # descripción
    "1",                      # cantidad
    "50000",                 # precio unitario
    "1",                      # IVA 10%
    "n",                      # no agregar otro ítem
]


def test_interactive_builds_nota_credito(monkeypatch):
    cdc = "0" * 44
    answers = ["2"] + _COMMON_HEAD + ["2", cdc, "s"]
    _scripted_input(monkeypatch, answers)

    payload = build_documento_interactive()

    assert payload["tipoDocumento"] == "NOTA_DE_CREDITO_ELECTRONICA"
    assert payload["motivoEmision"] == "DEVOLUCION"
    assert payload["documentoAsociado"] == {"tipoDocumento": "ELECTRONICO", "cdc": cdc}
    # NC/ND must not carry factura-only fields.
    assert "condicionOperacion" not in payload
    assert "condicionPago" not in payload
    assert len(payload["items"]) == 1


def test_interactive_builds_nota_debito(monkeypatch):
    cdc = "1" * 44
    # motivo "8" = AJUSTE_DE_PRECIO
    answers = ["3"] + _COMMON_HEAD + ["8", cdc, "s"]
    _scripted_input(monkeypatch, answers)

    payload = build_documento_interactive()

    assert payload["tipoDocumento"] == "NOTA_DE_DEBITO_ELECTRONICA"
    assert payload["motivoEmision"] == "AJUSTE_DE_PRECIO"
    assert payload["documentoAsociado"]["cdc"] == cdc


def test_interactive_builds_factura(monkeypatch):
    # motivo/CDC prompts are replaced by the pago prompt for a factura.
    answers = ["1"] + _COMMON_HEAD + ["1", "s"]  # tipo pago EFECTIVO, confirmar
    _scripted_input(monkeypatch, answers)

    payload = build_documento_interactive()

    assert payload["tipoDocumento"] == "FACTURA_ELECTRONICA"
    assert payload["condicionOperacion"] == "CONTADO"
    assert payload["condicionPago"]["tipoPago"] == "EFECTIVO"
    assert "motivoEmision" not in payload
    assert "documentoAsociado" not in payload


def test_build_factura_interactive_is_alias():
    assert build_factura_interactive is build_documento_interactive
