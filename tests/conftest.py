import pytest


@pytest.fixture
def minimal_valid_payload():
    return {
        "tipoDocumento": "FACTURA_ELECTRONICA",
        "tipoEmision": "NORMAL",
        "fechaEmision": "2026-05-09T10:00:00",
        "numeroEstablecimiento": "001",
        "puntoExpedicion": "001",
        "monedaOperacion": "PYG",
        "condicionOperacion": "CONTADO",
        "receptor": {
            "tipoContribuyente": "NO_CONTRIBUYENTE",
            "tipoOperacion": "B2C",
            "tipoDocumento": "CEDULA_PARAGUAYA",
            "numeroDocumento": "1234567",
            "nombreRazonSocial": "Cliente Final",
        },
        "items": [
            {
                "descripcion": "Servicio de prueba",
                "cantidad": 1,
                "precioUnitario": 100000,
                "tasaIVA": 10,
                "afectacionTributaria": "GRAVADO_IVA",
            }
        ],
    }
