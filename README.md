<img src="src/sifende-logo.svg" alt="Sifende"/>

# Sifende CLI

CLI en Python para testear/explorar integración con la API de facturación electrónica
[Sifende](https://www.sifende.com.py) (Paraguay / SIFEN).

Implementa los flujos típicos contra `https://api.sifende.com.py/api/v1/`:
emitir documentos, consultar estado, descargar el KuDE (PDF), cancelar y
inutilizar rangos de numeración. Sólo usa la stdlib + `requests`.

## Quickstart

```bash
make setup                       # crea venv, instala deps, prepara .env
$EDITOR .env                     # poné tu SIFENDE_API_KEY
make emitir FILE=sample_factura.json
```

O sin Make:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env             # editá .env con tu API key
python sifende.py emitir --file sample_factura.json
```

## Configuración

Necesitás una API key de Sifende — [cómo crearla](https://www.sifende.com.py/docs/inicio-rapido/paso-1-credenciales#14-crear-tu-api-key).

Variables soportadas en `.env`:

| Variable             | Default                                       |
|----------------------|-----------------------------------------------|
| `SIFENDE_API_KEY`    | (requerido)                                   |
| `SIFENDE_BASE_URL`   | `https://api.sifende.com.py/api/v1/`          |
| `SIFENDE_TIMEOUT_S`  | `30`                                          |

## Comandos

| Operación | Make | Python |
|-----------|------|--------|
| Emitir (archivo) | `make emitir FILE=factura.json` | `python sifende.py emitir --file factura.json` |
| Emitir (interactivo) | `make emitir-i` | `python sifende.py emitir` |
| Nota de crédito | `make nota-credito FILE_NC=nc.json` | `python sifende.py emitir --file nc.json` |
| Nota de débito | `make nota-debito FILE_ND=nd.json` | `python sifende.py emitir --file nd.json` |
| Consultar estado | `make estado CDC=<cdc>` | `python sifende.py estado <cdc>` |
| Descargar KuDE | `make kude CDC=<cdc> OUT=factura.pdf` | `python sifende.py kude <cdc> --out factura.pdf` |
| Cancelar | `make cancelar CDC=<cdc> MOTIVO="..."` | `python sifende.py cancelar <cdc> --motivo "..."` |
| Inutilizar | `make inutilizar TIPO=1 EST=001 PE=001 TIMBRADO=<t> DESDE=1 HASTA=3 MOTIVO="..."` | `python sifende.py inutilizar --tipo-documento 1 --establecimiento 001 --punto-expedicion 001 --numero-timbrado <t> --desde 1 --hasta 3 --motivo "..."` |
| Debug HTTP | `make debug FILE=factura.json` | `python sifende.py --debug emitir --file factura.json` |

Flags globales disponibles en todos los comandos: `--quiet`, `--json`, `--debug`, `--api-key`, `--base-url`.
Con Make se pasan como `EXTRA="--json"`.

La inutilización admite rangos de 2 a 1000 números por evento, conforme a las
restricciones de SIFEN. Una respuesta HTTP exitosa cuyo evento termine en
`RECHAZADO` o con un código distinto de `0600` devuelve exit code `2`.

Al aprobar un documento, la CLI guarda automáticamente `documentos/{cdc}/` con `payload.json`, `response.json` y `kude.pdf`.

### Notas de crédito y débito

Las notas de crédito (`NOTA_DE_CREDITO_ELECTRONICA`) y débito
(`NOTA_DE_DEBITO_ELECTRONICA`) usan el mismo comando `emitir`. Respecto a una
factura, requieren dos campos extra y **no** llevan `condicionOperacion`/`condicionPago`:

- `motivoEmision`: uno de `DEVOLUCION`, `DEVOLUCION_Y_AJUSTES_DE_PRECIOS`,
  `DESCUENTO`, `BONIFICACION`, `CREDITO_INCOBRABLE`, `RECUPERO_DE_COSTO`,
  `RECUPERO_DE_GASTO`, `AJUSTE_DE_PRECIO`.
- `documentoAsociado`: la referencia al DE original. Hoy sólo se admite
  `{"tipoDocumento": "ELECTRONICO", "cdc": "<44 dígitos>"}`, donde el CDC es el
  de una factura ya aprobada.

Hay ejemplos en `sample_nota_credito.json` y `sample_nota_debito.json` — reemplazá
el `cdc` del `documentoAsociado` por el de una factura real antes de emitir. El
modo interactivo (`make emitir-i`) también guía la carga de estos campos cuando
elegís tipo 2 (nota de crédito) o 3 (nota de débito).


## Estructura del proyecto

```
sifende_cli/
├── ARCHITECTURE.md
├── README.md
├── Makefile
├── requirements.txt
├── .env.example
├── sample_factura.json
├── sample_nota_credito.json
├── sample_nota_debito.json
├── sifende.py
└── sifende/
    ├── __main__.py
    ├── cli.py
    ├── config.py
    ├── client.py
    ├── errors.py
    ├── models.py
    ├── polling.py
    ├── interactive.py
    ├── commands/{emitir,estado,kude,cancelar,inutilizar}.py
    └── utils/{formatting,validation,io}.py
```
