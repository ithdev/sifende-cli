# Sifende CLI — Makefile
# El camino feliz es:
#   make setup → editá .env → make emitir

PYTHON   ?= python3
VENV     := .venv
PY       := $(VENV)/bin/python
PIP      := $(VENV)/bin/pip
SIFENDE  := $(PY) sifende.py

# Variables por comando (se pueden pisar desde la CLI). Los defaults permiten
# que `make emitir` funcione directo después de `make setup` con el sample incluido.
FILE     ?= sample_factura.json
FILE_NC  ?= sample_nota_credito.json
FILE_ND  ?= sample_nota_debito.json
CDC      ?=
OUT      ?=
MOTIVO   ?=
TIPO     ?=
EST      ?=
PE       ?=
TIMBRADO ?=
DESDE    ?=
HASTA    ?=

# Flags extra que se reenvían a la CLI: `make emitir EXTRA="--no-wait --json"`.
EXTRA    ?=

.DEFAULT_GOAL := help

.PHONY: help setup install env emitir emitir-i nota-credito nota-debito estado \
        kude cancelar inutilizar emit-and-pdf clean

help: ## Mostrar esta ayuda
	@echo "Sifende CLI — comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk -F':.*?## ' '{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Variables (pisá con VAR=valor):"
	@echo "  FILE=$(FILE)"
	@echo "  FILE_NC=$(FILE_NC)  FILE_ND=$(FILE_ND)"
	@echo "  CDC, OUT, MOTIVO, TIPO, EST, PE, DESDE, HASTA, EXTRA"

# Guard de variable requerida. Los targets listan `guard-FOO` como prerequisito
# y Make lo resuelve con esta regla de patrón. El error apunta a `make help`.
guard-%:
	@[ "${${*}}" ] || { echo "ERROR: falta $*=... — probá 'make help'"; exit 2; }

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)

install: $(VENV)/bin/activate ## Instalar dependencias en .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

setup: install ## Crear venv, instalar deps y preparar .env
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Creado .env desde .env.example — editá y agregá SIFENDE_API_KEY."; \
	else \
		echo ".env ya existe — sin cambios."; \
	fi
	@echo "Listo. Próximo paso: editá .env y luego ejecutá 'make emitir'."

debug: ## Emitir con traza HTTP completa (API key enmascarada)
	$(SIFENDE) --debug emitir --file $(FILE) $(EXTRA)

emitir: ## Emitir documento (FILE=sample_factura.json por defecto)
	$(SIFENDE) emitir --file $(FILE) $(EXTRA)

emitir-i: ## Emitir en modo interactivo (sin --file)
	$(SIFENDE) emitir $(EXTRA)

nota-credito: ## Emitir nota de crédito (FILE_NC=sample_nota_credito.json por defecto)
	$(SIFENDE) emitir --file $(FILE_NC) $(EXTRA)

nota-debito: ## Emitir nota de débito (FILE_ND=sample_nota_debito.json por defecto)
	$(SIFENDE) emitir --file $(FILE_ND) $(EXTRA)

estado: guard-CDC ## Consultar estado — make estado CDC=xxxx
	$(SIFENDE) estado $(CDC) $(EXTRA)

kude: guard-CDC ## Descargar KuDE PDF — make kude CDC=xxxx [OUT=ruta.pdf]
	$(SIFENDE) kude $(CDC) $(if $(OUT),--out $(OUT)) $(EXTRA)

cancelar: guard-CDC guard-MOTIVO ## Cancelar documento — make cancelar CDC=xxxx MOTIVO="..."
	$(SIFENDE) cancelar $(CDC) --motivo "$(MOTIVO)" $(EXTRA)

inutilizar: guard-TIPO guard-EST guard-PE guard-TIMBRADO guard-DESDE guard-HASTA guard-MOTIVO ## Inutilizar rango — TIPO=1 EST=001 PE=001 TIMBRADO=xxx DESDE=x HASTA=y MOTIVO="..."
	$(SIFENDE) inutilizar \
		--tipo-documento $(TIPO) \
		--establecimiento $(EST) \
		--punto-expedicion $(PE) \
		--numero-timbrado $(TIMBRADO) \
		--desde $(DESDE) --hasta $(HASTA) \
		--motivo "$(MOTIVO)" $(EXTRA)

emit-and-pdf: guard-FILE ## Emitir y copiar KuDE a OUT=ruta (default: emitida.pdf), además de documentos/{cdc}/
	$(SIFENDE) emitir --file $(FILE) --save-pdf $(or $(OUT),emitida.pdf) $(EXTRA)

clean: ## Eliminar venv y cachés
	rm -rf $(VENV) **/__pycache__ .pytest_cache *.pdf
	@echo "limpio"
