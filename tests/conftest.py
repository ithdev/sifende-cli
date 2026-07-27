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


@pytest.fixture
def minimal_valid_nota_payload():
    """A NC/ND payload: no condicionOperacion, but motivoEmision + documentoAsociado."""
    return {
        "tipoDocumento": "NOTA_DE_CREDITO_ELECTRONICA",
        "tipoEmision": "NORMAL",
        "fechaEmision": "2026-05-09T11:00:00",
        "numeroEstablecimiento": "001",
        "puntoExpedicion": "001",
        "monedaOperacion": "PYG",
        "motivoEmision": "DEVOLUCION",
        "documentoAsociado": {
            "tipoDocumento": "ELECTRONICO",
            "cdc": "0" * 44,
        },
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
