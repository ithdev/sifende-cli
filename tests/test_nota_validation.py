import copy

import pytest

from sifende.errors import ValidationError
from sifende.utils.validation import (
    validate_documento_asociado,
    validate_documento_payload,
    validate_factura_payload,
)


def test_accepts_valid_nota_credito(minimal_valid_nota_payload):
    assert validate_documento_payload(minimal_valid_nota_payload) is minimal_valid_nota_payload


def test_nota_debito_also_accepted(minimal_valid_nota_payload):
    payload = copy.deepcopy(minimal_valid_nota_payload)
    payload["tipoDocumento"] = "NOTA_DE_DEBITO_ELECTRONICA"
    payload["motivoEmision"] = "AJUSTE_DE_PRECIO"
    assert validate_documento_payload(payload) is payload


def test_nota_does_not_require_condicion_operacion(minimal_valid_nota_payload):
    # A NC/ND must validate even though it has no condicionOperacion.
    assert "condicionOperacion" not in minimal_valid_nota_payload
    validate_documento_payload(minimal_valid_nota_payload)


def test_nota_missing_motivo_raises(minimal_valid_nota_payload):
    payload = copy.deepcopy(minimal_valid_nota_payload)
    payload.pop("motivoEmision")
    with pytest.raises(ValidationError) as exc:
        validate_documento_payload(payload)
    assert "motivoEmision" in str(exc.value)


def test_nota_invalid_motivo_raises(minimal_valid_nota_payload):
    payload = copy.deepcopy(minimal_valid_nota_payload)
    payload["motivoEmision"] = "NO_EXISTE"
    with pytest.raises(ValidationError) as exc:
        validate_documento_payload(payload)
    assert "motivoEmision" in str(exc.value)


def test_nota_missing_documento_asociado_raises(minimal_valid_nota_payload):
    payload = copy.deepcopy(minimal_valid_nota_payload)
    payload.pop("documentoAsociado")
    with pytest.raises(ValidationError) as exc:
        validate_documento_payload(payload)
    assert "documentoAsociado" in str(exc.value)


def test_nota_documento_asociado_bad_cdc_raises(minimal_valid_nota_payload):
    payload = copy.deepcopy(minimal_valid_nota_payload)
    payload["documentoAsociado"]["cdc"] = "123"
    with pytest.raises(ValidationError) as exc:
        validate_documento_payload(payload)
    assert "cdc" in str(exc.value)


def test_documento_asociado_non_electronico_rejected():
    with pytest.raises(ValidationError) as exc:
        validate_documento_asociado({"tipoDocumento": "IMPRESO", "cdc": "0" * 44})
    assert "ELECTRONICO" in str(exc.value)


def test_factura_still_requires_condicion_operacion(minimal_valid_payload):
    payload = copy.deepcopy(minimal_valid_payload)
    payload.pop("condicionOperacion")
    with pytest.raises(ValidationError) as exc:
        validate_documento_payload(payload)
    assert "condicionOperacion" in str(exc.value)


def test_validate_factura_payload_is_alias():
    assert validate_factura_payload is validate_documento_payload
