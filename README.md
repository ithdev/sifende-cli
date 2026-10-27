<img src="src/sifende-logo.svg" alt="Sifende"/>

# Sifende CLI

![CI](https://github.com/ithdev/sifende-cli/actions/workflows/ci.yml/badge.svg)
![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-blue)

CLI en Python para probar la API de [Sifende](https://www.sifende.com.py) desde la terminal: emitir facturas y notas,
consultar su estado, descargar el KuDE, cancelar e inutilizar numeración en SIFEN.

Sirve para explorar la API antes de integrarla. Para integrarla en tu sistema, usá un SDK:
[`@sifende/sdk`](https://github.com/ithdev/sifende-node) (TypeScript) o
[`sifende-go`](https://github.com/ithdev/sifende-go).

## Requisitos

- Python 3.11 o posterior. Solo depende de `requests`.
- Una API key de Sifende ([cómo crearla](https://www.sifende.com.py/docs/inicio-rapido/paso-1-credenciales#14-crear-tu-api-key)).
  Para probar sin enviar nada a SIFEN, usá una de Sandbox (`sk_sandbox_`).

## Primeros pasos

```bash
git clone https://github.com/ithdev/sifende-cli
cd sifende-cli
make setup                       # crea el venv, instala dependencias y copia .env.example a .env
$EDITOR .env                     # poné tu SIFENDE_API_KEY
make emitir                      # emite sample_factura.json y espera la respuesta de SIFEN
```

Sin Make:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env             # poné tu SIFENDE_API_KEY
python sifende.py emitir --file sample_factura.json
```

Cuando SIFEN aprueba el documento, la CLI guarda `documentos/{cdc}/` con `payload.json`, `response.json` y `kude.pdf`.

## Configuración

Variables de `.env`:

| Variable | Por defecto |
|---|---|
| `SIFENDE_API_KEY` | Obligatoria. |
| `SIFENDE_BASE_URL` | `https://api.sifende.com.py/api/v1/` |
| `SIFENDE_TIMEOUT_S` | `30` |

## Comandos

| Operación | Make | Python |
|---|---|---|
| Emitir desde un archivo | `make emitir FILE=factura.json` | `python sifende.py emitir --file factura.json` |
| Emitir en modo interactivo | `make emitir-i` | `python sifende.py emitir` |
| Nota de crédito | `make nota-credito FILE_NC=nc.json` | `python sifende.py emitir --file nc.json` |
| Nota de débito | `make nota-debito FILE_ND=nd.json` | `python sifende.py emitir --file nd.json` |
| Consultar estado | `make estado CDC=<cdc>` | `python sifende.py estado <cdc>` |
| Descargar KuDE | `make kude CDC=<cdc> OUT=factura.pdf` | `python sifende.py kude <cdc> --out factura.pdf` |
| KuDE en ticket | `make kude CDC=<cdc> FORMATO=ticket ANCHO=58` | `python sifende.py kude <cdc> --formato ticket --ancho 58` |
| Cancelar | `make cancelar CDC=<cdc> MOTIVO="..."` | `python sifende.py cancelar <cdc> --motivo "..."` |
| Inutilizar | `make inutilizar TIPO=1 EST=001 PE=001 TIMBRADO=<t> DESDE=1 HASTA=3 MOTIVO="..."` | `python sifende.py inutilizar --tipo-documento 1 --establecimiento 001 --punto-expedicion 001 --numero-timbrado <t> --desde 1 --hasta 3 --motivo "..."` |
| Ver el tráfico HTTP | `make debug FILE=factura.json` | `python sifende.py --debug emitir --file factura.json` |

`make help` lista todos los comandos.

Todos los comandos aceptan `--quiet`, `--json`, `--debug`, `--api-key` y `--base-url`. Con Make, se pasan en `EXTRA`:
`make emitir EXTRA="--json"`. `--debug` enmascara la API key. `emitir --no-wait` devuelve el CDC sin esperar la
respuesta de SIFEN.

La inutilización admite rangos de 2 a 1000 números por evento, como exige SIFEN.

### KuDE en cinta de papel

`kude --formato ticket` descarga el KuDE en cinta de papel para impresoras
térmicas, con `--ancho 80` (default) o `--ancho 58`. `--formato ticket-resumen`
omite el detalle de ítems e impuestos, para cuando el cliente pide el resumen. Sólo
está disponible para facturas y notas de crédito o débito; el KuDE A4 sigue siendo
el que se guarda y se envía por email.

### Notas de crédito y débito

Las notas de crédito (`NOTA_DE_CREDITO_ELECTRONICA`) y de débito (`NOTA_DE_DEBITO_ELECTRONICA`) usan el mismo comando
`emitir`. A diferencia de una factura, no llevan `condicionOperacion` ni `condicionPago`, y requieren dos campos más:

- `motivoEmision`: `DEVOLUCION`, `DEVOLUCION_Y_AJUSTES_DE_PRECIOS`, `DESCUENTO`, `BONIFICACION`,
  `CREDITO_INCOBRABLE`, `RECUPERO_DE_COSTO`, `RECUPERO_DE_GASTO` o `AJUSTE_DE_PRECIO`.
- `documentoAsociado`: el documento original. Por ahora solo se admite
  `{"tipoDocumento": "ELECTRONICO", "cdc": "<44 dígitos>"}`, con el CDC de una factura aprobada.

Hay ejemplos en `sample_nota_credito.json` y `sample_nota_debito.json`: antes de emitir, reemplazá el `cdc` del
`documentoAsociado` por el de una factura real. El modo interactivo también pide estos campos cuando elegís el tipo 2
(nota de crédito) o 3 (nota de débito).

### Códigos de salida

| Código | Significado |
|---|---|
| `0` | La operación terminó bien. |
| `1` | Error no clasificado. |
| `2` | SIFEN rechazó el documento o el evento (también un evento con código distinto de `0600`). |
| `3` | Se agotó la espera de la respuesta de SIFEN. Consultá el estado más tarde con `estado`. |
| `4` | Datos o configuración inválidos (por ejemplo, falta la API key). |
| `5` | Error de la API o de red: autenticación, documento inexistente, HTTP o conexión. |
| `130` | Cancelado con Ctrl+C. |

## Desarrollo

```bash
pip install requests pytest
pytest tests/
```

La CI corre los tests con Python 3.11 y 3.12. Los cambios se anotan en el [CHANGELOG](CHANGELOG.md).

## Soporte

- Errores de la CLI: abrí un [issue](https://github.com/ithdev/sifende-cli/issues).
- Tu cuenta, tus documentos o la API: escribinos a [soporte@sifende.com.py](mailto:soporte@sifende.com.py).
- La documentación de la API está en [sifende.com.py/docs](https://www.sifende.com.py/docs).

## Licencia

[MIT](LICENSE).
