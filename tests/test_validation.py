import copy

import pytest

from sifende.errors import ValidationError
from sifende.utils.validation import validate_factura_payload


def test_accepts_valid_b2c_payload(minimal_valid_payload):
    assert validate_factura_payload(minimal_valid_payload) is minimal_valid_payload



def test_missing_receptor_raises(minimal_valid_payload):
    payload = copy.deepcopy(minimal_valid_payload)
    payload.pop("receptor")
    with pytest.raises(ValidationError) as exc:
        validate_factura_payload(payload)
    assert "receptor" in str(exc.value)


def test_empty_items_list_raises(minimal_valid_payload):
    payload = copy.deepcopy(minimal_valid_payload)
    payload["items"] = []
    with pytest.raises(ValidationError) as exc:
        validate_factura_payload(payload)
    assert "items" in str(exc.value)


def test_missing_items_raises(minimal_valid_payload):
    payload = copy.deepcopy(minimal_valid_payload)
    payload.pop("items")
    with pytest.raises(ValidationError) as exc:
        validate_factura_payload(payload)
    assert "items" in str(exc.value)


def test_receptor_missing_tipo_contribuyente_raises(minimal_valid_payload):
    payload = copy.deepcopy(minimal_valid_payload)
    payload["receptor"].pop("tipoContribuyente")
    with pytest.raises(ValidationError) as exc:
        validate_factura_payload(payload)
    assert "tipoContribuyente" in str(exc.value)


def test_receptor_missing_nombre_razon_social_raises(minimal_valid_payload):
    payload = copy.deepcopy(minimal_valid_payload)
    payload["receptor"].pop("nombreRazonSocial")
    with pytest.raises(ValidationError) as exc:
        validate_factura_payload(payload)
    assert "nombreRazonSocial" in str(exc.value)


def test_item_missing_descripcion_raises(minimal_valid_payload):
    payload = copy.deepcopy(minimal_valid_payload)
    payload["items"][0].pop("descripcion")
    with pytest.raises(ValidationError) as exc:
        validate_factura_payload(payload)
    assert "descripcion" in str(exc.value)
