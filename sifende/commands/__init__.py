"""Command modules. Each exports register(subparsers) and run(args, client)."""

from . import cancelar, emitir, estado, inutilizar, kude

ALL_COMMANDS = (
    ("emitir", emitir),
    ("estado", estado),
    ("kude", kude),
    ("cancelar", cancelar),
    ("inutilizar", inutilizar),
)
