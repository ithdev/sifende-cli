"""I/O helpers: JSON load, PDF save, validated stdin prompt."""

from __future__ import annotations

import json
import os
import sys
from typing import Callable, Optional

from ..errors import ConfigError, ValidationError


def load_json_payload(path: str) -> dict:
    if not os.path.isfile(path):
        raise ConfigError(f"archivo no encontrado: {path}")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValidationError("payload", f"JSON inválido en {path}: {exc.msg} (línea {exc.lineno})")
    except OSError as exc:
        raise ConfigError(f"no se pudo leer {path}: {exc}")
    if not isinstance(data, dict):
        raise ValidationError("payload", "el JSON raíz debe ser un objeto")
    return data


def save_pdf(data: bytes, path: str) -> str:
    if not isinstance(data, (bytes, bytearray)) or not data:
        raise ValidationError("kude", "respuesta PDF vacía")
    try:
        with open(path, "wb") as fh:
            fh.write(data)
    except OSError as exc:
        raise ConfigError(f"no se pudo escribir {path}: {exc}")
    return path


def save_document_folder(
    cdc: str,
    payload: dict,
    response: dict,
    pdf: Optional[bytes] = None,
    *,
    base: str = "documentos",
) -> str:
    """Create documentos/{cdc}/ and write payload.json, response.json, kude.pdf."""
    folder = os.path.join(base, cdc)
    try:
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "payload.json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        with open(os.path.join(folder, "response.json"), "w", encoding="utf-8") as fh:
            json.dump(response, fh, ensure_ascii=False, indent=2)
        if pdf:
            with open(os.path.join(folder, "kude.pdf"), "wb") as fh:
                fh.write(pdf)
    except OSError as exc:
        raise ConfigError(f"no se pudo guardar en {folder}: {exc}")
    return folder


def prompt(
    msg: str,
    *,
    default: Optional[str] = None,
    validator: Optional[Callable[[str], str]] = None,
    allow_empty: bool = False,
) -> str:
    """Read a line from stdin, with optional default and re-prompt on failure.

    `validator` may raise ValidationError; we catch it locally and re-prompt
    so the user fixes the typo without restarting the whole interactive run.
    """
    suffix = f" [{default}]" if default is not None else ""
    while True:
        try:
            raw = input(f"{msg}{suffix}: ")
        except EOFError:
            raise KeyboardInterrupt
        value = raw.strip()
        if not value:
            if default is not None:
                value = default
            elif allow_empty:
                return ""
            else:
                print("  ! requerido", file=sys.stderr)
                continue
        if validator is None:
            return value
        try:
            return validator(value)
        except ValidationError as exc:
            print(f"  ! {exc.message}", file=sys.stderr)
