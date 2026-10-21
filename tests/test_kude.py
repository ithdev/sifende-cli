from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from sifende.client import SifendeClient
from sifende.commands.kude import run
from sifende.config import Config
from sifende.errors import ValidationError

CDC = "01800123451001001000000122026042710000000006"
PDF = b"%PDF-1.4 synthetic"


def _make_args(tmp_path, *, formato="a4", ancho=None, out=None):
    return SimpleNamespace(
        cdc=CDC,
        formato=formato,
        ancho=ancho,
        out=str(tmp_path / out) if out else None,
        json=False,
        quiet=True,
    )


def test_a4_uses_existing_endpoint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    client = MagicMock()
    client.kude.return_value = PDF
    assert run(_make_args(tmp_path), client) == 0
    client.kude.assert_called_once_with(CDC)
    assert not client.kude_ticket.called
    assert (tmp_path / f"{CDC}.pdf").read_bytes() == PDF


@pytest.mark.parametrize(
    "formato,ancho,resumen,ancho_esperado",
    [("ticket", None, False, 80), ("ticket", 58, False, 58), ("ticket-resumen", 80, True, 80)],
)
def test_ticket_formats(tmp_path, monkeypatch, formato, ancho, resumen, ancho_esperado):
    monkeypatch.chdir(tmp_path)
    client = MagicMock()
    client.kude_ticket.return_value = PDF
    assert run(_make_args(tmp_path, formato=formato, ancho=ancho), client) == 0
    client.kude_ticket.assert_called_once_with(CDC, ancho=ancho_esperado, resumen=resumen)
    assert (tmp_path / f"{CDC}-{formato}.pdf").read_bytes() == PDF


def test_ancho_with_a4_is_rejected_locally(tmp_path):
    client = MagicMock()
    with pytest.raises(ValidationError) as exc:
        run(_make_args(tmp_path, ancho=58), client)
    assert exc.value.field == "ancho"
    assert not client.kude.called


def test_client_builds_ticket_url():
    client = SifendeClient(Config(api_key="k", base_url="https://api.example.com/api/v1/", timeout_s=5))
    response = MagicMock(status_code=200, content=PDF, ok=True)
    client._session.request = MagicMock(return_value=response)
    assert client.kude_ticket(CDC, ancho=58, resumen=True) == PDF
    method, url = client._session.request.call_args.args
    assert method == "GET"
    assert url == f"https://api.example.com/api/v1/documento-electronico/{CDC}/kude/ticket?ancho=58&resumen=true"
    assert client._session.request.call_args.kwargs["headers"]["Accept"] == "application/pdf"
