<img src="src/sifende-logo.svg" alt="Sifende"/>

# Sifende CLI

CLI en Python para integrarse con el API de facturación electrónica
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

La API key se busca en este orden (gana el primero que se encuentre):

1. Flag `--api-key`
2. Variable de entorno `SIFENDE_API_KEY`
3. Archivo `.env` en el directorio actual
4. Archivo `.env` en la raíz del paquete

La key **nunca** se ecoa, ni en logs ni en mensajes de error. El header
`Authorization` se omite explícitamente al renderizar `HttpError`.

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
| Consultar estado | `make estado CDC=<cdc>` | `python sifende.py estado <cdc>` |
| Descargar KuDE | `make kude CDC=<cdc> OUT=factura.pdf` | `python sifende.py kude <cdc> --out factura.pdf` |
| Cancelar | `make cancelar CDC=<cdc> MOTIVO="..."` | `python sifende.py cancelar <cdc> --motivo "..."` |
| Inutilizar | `make inutilizar TIPO=1 EST=001 PE=001 TIMBRADO=<t> DESDE=1 HASTA=3 MOTIVO="..."` | `python sifende.py inutilizar --tipo-documento 1 --establecimiento 001 --punto-expedicion 001 --numero-timbrado <t> --desde 1 --hasta 3 --motivo "..."` |
| Debug HTTP | `make debug FILE=factura.json` | `python sifende.py --debug emitir --file factura.json` |

Flags globales disponibles en todos los comandos: `--quiet`, `--json`, `--debug`, `--api-key`, `--base-url`.
Con Make se pasan como `EXTRA="--json"`.

Al aprobar un documento, la CLI guarda automáticamente `documentos/{cdc}/` con `payload.json`, `response.json` y `kude.pdf`.


## Estructura del proyecto

```
sifende_cli/
├── ARCHITECTURE.md
├── README.md
├── Makefile
├── requirements.txt
├── .env.example
├── sample_factura.json
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
