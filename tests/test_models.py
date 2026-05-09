from sifende.models import (
    Estado,
    EmitirResponse,
    EstadoResponse,
    SUCCESS_ESTADOS,
    TERMINAL_ESTADOS,
)


def test_estado_constants():
    assert Estado.PENDIENTE == "PENDIENTE"
    assert Estado.EN_LOTE == "EN_LOTE"
    assert Estado.ENVIADO == "ENVIADO"
    assert Estado.APROBADO == "APROBADO"
    assert Estado.APROBADO_OBSERVACION == "APROBADO_OBSERVACION"
    assert Estado.RECHAZADO == "RECHAZADO"
    assert Estado.ERROR == "ERROR"
    assert Estado.CANCELADO == "CANCELADO"


def test_terminal_estados_membership():
    assert Estado.APROBADO in TERMINAL_ESTADOS
    assert Estado.APROBADO_OBSERVACION in TERMINAL_ESTADOS
    assert Estado.RECHAZADO in TERMINAL_ESTADOS
    assert Estado.ERROR in TERMINAL_ESTADOS
    assert Estado.CANCELADO in TERMINAL_ESTADOS
    assert Estado.PENDIENTE not in TERMINAL_ESTADOS


def test_success_estados_only_aprobado():
    assert Estado.APROBADO in SUCCESS_ESTADOS
    assert len(SUCCESS_ESTADOS) == 1
    assert Estado.APROBADO_OBSERVACION not in SUCCESS_ESTADOS


def test_emitir_response_from_api():
    payload = {
        "cdc": "01" * 22,
        "estado": "PENDIENTE",
        "id": "abc-123",
        "statusUrl": "https://api.example.com/status/1",
        "kudeUrl": "https://api.example.com/kude/1",
        "qrUrl": "https://api.example.com/qr/1",
    }
    r = EmitirResponse.from_api(payload)
    assert r.cdc == "01" * 22
    assert r.estado == "PENDIENTE"
    assert r.id == "abc-123"
    assert r.status_url == "https://api.example.com/status/1"
    assert r.kude_url == "https://api.example.com/kude/1"
    assert r.qr_url == "https://api.example.com/qr/1"
    assert r.raw == payload


def test_emitir_response_to_dict_roundtrips_keys():
    payload = {
        "cdc": "01" * 22,
        "estado": "APROBADO",
        "id": "abc-123",
        "statusUrl": "u1",
        "kudeUrl": "u2",
        "qrUrl": "u3",
    }
    r = EmitirResponse.from_api(payload)
    out = r.to_dict()
    assert set(out.keys()) == {"cdc", "estado", "id", "statusUrl", "kudeUrl", "qrUrl"}
    assert out["cdc"] == payload["cdc"]
    assert out["estado"] == payload["estado"]
    assert out["statusUrl"] == "u1"
    assert out["kudeUrl"] == "u2"
    assert out["qrUrl"] == "u3"


def test_estado_response_is_terminal():
    assert EstadoResponse(cdc="x", estado=Estado.APROBADO).is_terminal is True
    assert EstadoResponse(cdc="x", estado=Estado.RECHAZADO).is_terminal is True
    assert EstadoResponse(cdc="x", estado=Estado.ERROR).is_terminal is True
    assert EstadoResponse(cdc="x", estado=Estado.PENDIENTE).is_terminal is False
    assert EstadoResponse(cdc="x", estado=Estado.EN_LOTE).is_terminal is False


def test_estado_response_is_success():
    assert EstadoResponse(cdc="x", estado=Estado.APROBADO).is_success is True
    assert EstadoResponse(cdc="x", estado=Estado.APROBADO_OBSERVACION).is_success is False
    assert EstadoResponse(cdc="x", estado=Estado.RECHAZADO).is_success is False
    assert EstadoResponse(cdc="x", estado=Estado.PENDIENTE).is_success is False
