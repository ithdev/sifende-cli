from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from sifende.commands.inutilizar import run
from sifende.errors import ValidationError


def _make_args(*, desde, hasta):
    return SimpleNamespace(
        tipo_documento=1,
        establecimiento="001",
        punto_expedicion="001",
        numero_timbrado="12345678",
        desde=desde,
        hasta=hasta,
        motivo="motivo de prueba",
        json=False,
        quiet=True,
    )


def test_range_of_4_passes_guard():
    client = MagicMock()
    client.inutilizar.return_value = {}
    args = _make_args(desde=1, hasta=4)
    rc = run(args, client)
    assert rc == 0
    assert client.inutilizar.called


def test_range_of_5_raises():
    client = MagicMock()
    args = _make_args(desde=1, hasta=5)
    with pytest.raises(ValidationError) as exc:
        run(args, client)
    assert "máximo 4" in str(exc.value)
    assert not client.inutilizar.called


def test_range_of_100_raises():
    client = MagicMock()
    args = _make_args(desde=1, hasta=100)
    with pytest.raises(ValidationError) as exc:
        run(args, client)
    assert "máximo 4" in str(exc.value)
    assert not client.inutilizar.called


def test_desde_below_one_raises():
    client = MagicMock()
    args = _make_args(desde=0, hasta=3)
    with pytest.raises(ValidationError) as exc:
        run(args, client)
    assert "1 ≤ desde" in str(exc.value)


def test_desde_greater_than_hasta_raises():
    client = MagicMock()
    args = _make_args(desde=5, hasta=3)
    with pytest.raises(ValidationError) as exc:
        run(args, client)
    assert "desde ≤ hasta" in str(exc.value)
