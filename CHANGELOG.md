# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Emisión de **notas de crédito** (`NOTA_DE_CREDITO_ELECTRONICA`) y **notas de
  débito** (`NOTA_DE_DEBITO_ELECTRONICA`) vía el comando `emitir`, tanto por
  archivo como en modo interactivo. El wizard pide `motivoEmision` y el CDC del
  `documentoAsociado` (la factura original) cuando se elige NC/ND.
- Samples `sample_nota_credito.json` y `sample_nota_debito.json`.
- Targets `make nota-credito` y `make nota-debito` (con variables `FILE_NC` /
  `FILE_ND`).

### Changed

- La validación local ahora depende del `tipoDocumento`: la factura sigue
  requiriendo `condicionOperacion`; las NC/ND requieren `motivoEmision` (valor
  válido del enum SIFEN) y un `documentoAsociado` `ELECTRONICO` con CDC de 44
  dígitos. `validate_factura_payload` / `build_factura_interactive` se mantienen
  como alias de las nuevas `validate_documento_payload` /
  `build_documento_interactive`.

## [0.1.0] - 2026-05-09

Initial release.

### Added

- `emitir` command — emite un documento electrónico a partir de un archivo
  JSON (`--file`) o vía un builder interactivo cuando no se pasa `--file`.
  Tras el `POST` inicial, hace polling cada 3 s hasta un estado terminal
  (`APROBADO`, `RECHAZADO`, `ERROR`) o el timeout configurado.
- `estado` command — consulta puntual del estado de un CDC.
- `kude` command — descarga el KuDE (PDF representativo) de un documento ya
  aprobado, con `--out` para elegir la ruta destino.
- `cancelar` command — cancela un documento aprobado dando un motivo.
- `inutilizar` command — inutiliza un rango de numeración, con validación
  local que limita el rango a un máximo de 4 números por llamada.
- Auto-persistencia en `documentos/{cdc}/` cuando `emitir` termina en
  `APROBADO`: se guardan `payload.json`, `response.json` y `kude.pdf`.
- Modo `--debug` global para emitir el detalle de las requests/responses
  HTTP (con la `Authorization` redactada).
- Flags globales `--json` (salida estructurada apta para pipelines) y
  `--quiet` (silencia el ticker y los logs no esenciales).
- Códigos de salida documentados: `0` OK / APROBADO, `1` error inesperado,
  `2` RECHAZADO o ERROR, `3` timeout de polling, `4` validación local,
  `5` error HTTP / red, `130` interrumpido (Ctrl+C).
- `Makefile` con targets para `setup`, `emitir`, `estado`, `kude`,
  `cancelar` e `inutilizar`, equivalentes a invocar la CLI directamente.

[0.1.0]: https://example.com/sifende-cli/releases/tag/v0.1.0
