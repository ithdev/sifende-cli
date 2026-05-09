from sifende.errors import (
    AuthError,
    HttpError,
    NetworkError,
    RejectedError,
    ValidationError,
)


def test_http_error_stores_status_and_str_is_readable():
    err = HttpError(500, "internal boom", url="https://api.example.com/v1/emitir")
    assert err.status == 500
    s = str(err)
    assert "500" in s
    assert "internal boom" in s


def test_auth_error_is_http_error_subclass():
    err = AuthError(401, "unauthorized")
    assert isinstance(err, HttpError)
    assert err.status == 401


def test_network_error_str_includes_message():
    err = NetworkError("connection refused")
    assert "connection refused" in str(err)


def test_validation_error_stores_field_and_message():
    err = ValidationError("receptor", "campo requerido")
    assert err.field == "receptor"
    assert err.message == "campo requerido"
    assert "receptor" in str(err)
    assert "campo requerido" in str(err)


def test_rejected_error_stores_cdc_estado_mensaje():
    err = RejectedError("01" * 22, "RECHAZADO", "factura rechazada por SIFEN")
    assert err.cdc == "01" * 22
    assert err.estado == "RECHAZADO"
    assert err.mensaje_rechazo == "factura rechazada por SIFEN"
    assert "RECHAZADO" in str(err)
