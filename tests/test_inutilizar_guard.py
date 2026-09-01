from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from sifende.commands.inutilizar import run
from sifende.config import Config
from sifende.cli import main
from sifende.errors import RejectedError, ValidationError


APPROVED_RESPONSE = {
    "estadoEvento": "APROBADO",
    "codigoRespuesta": "0600",
    "mensajeRespuesta": "[0600] Evento registrado correctamente",
}


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


def test_range_of_2_passes_guard():
    client = MagicMock()
    client.inutilizar.return_value = APPROVED_RESPONSE
    args = _make_args(desde=1, hasta=2)
    rc = run(args, client)
    assert rc == 0
    assert client.inutilizar.called


def test_range_of_1000_passes_guard():
    client = MagicMock()
    client.inutilizar.return_value = APPROVED_RESPONSE
    args = _make_args(desde=1, hasta=1000)
    rc = run(args, client)
    assert rc == 0
    assert client.inutilizar.called


def test_range_of_1001_raises():
    client = MagicMock()
    args = _make_args(desde=1, hasta=1001)
    with pytest.raises(ValidationError) as exc:
        run(args, client)
    assert "máximo 1000" in str(exc.value)
    assert not client.inutilizar.called


def test_single_number_raises():
    client = MagicMock()
    args = _make_args(desde=4, hasta=4)
    with pytest.raises(ValidationError) as exc:
        run(args, client)
    assert "mínimo 2" in str(exc.value)
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


def test_rejected_event_raises_rejected_error():
    client = MagicMock()
    client.inutilizar.return_value = {
        "estadoEvento": "RECHAZADO",
        "codigoRespuesta": "4065",
        "mensajeRespuesta": "[4065] Existe DTE en el rango informado",
    }

    with pytest.raises(RejectedError) as exc:
        run(_make_args(desde=1008, hasta=1011), client)

    assert exc.value.cdc is None
    assert exc.value.estado == "RECHAZADO"
    assert "4065" in str(exc.value)


def test_approved_state_with_non_success_code_is_rejected():
    client = MagicMock()
    client.inutilizar.return_value = {
        "estadoEvento": "APROBADO",
        "codigoRespuesta": "9999",
        "mensajeRespuesta": "respuesta inconsistente",
    }

    with pytest.raises(RejectedError):
        run(_make_args(desde=1, hasta=2), client)


def test_cli_returns_exit_code_2_for_rejected_event(capsys):
    client = MagicMock()
    client.inutilizar.return_value = {
        "estadoEvento": "RECHAZADO",
        "codigoRespuesta": "4065",
        "mensajeRespuesta": "[4065] Existe DTE en el rango informado",
    }
    client_context = MagicMock()
    client_context.__enter__.return_value = client

    argv = [
        "inutilizar",
        "--tipo-documento", "1",
        "--establecimiento", "001",
        "--punto-expedicion", "001",
        "--numero-timbrado", "19046779",
        "--desde", "1008",
        "--hasta", "1011",
        "--motivo", "Error de sistema",
    ]

    with (
        patch("sifende.cli.load_config", return_value=Config("test-key", "https://example.test/")),
        patch("sifende.cli.SifendeClient", return_value=client_context),
    ):
        exit_code = main(argv)

    assert exit_code == 2
    assert "RECHAZADO" in capsys.readouterr().err
