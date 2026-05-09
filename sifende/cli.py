"""Top-level argparse setup and dispatcher."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .client import SifendeClient
from .commands import ALL_COMMANDS
from .config import load_config
from .errors import (
    AuthError,
    ConfigError,
    HttpError,
    NetworkError,
    NotFoundError,
    RejectedError,
    SifendeError,
    TimeoutError as PollTimeoutError,
    ValidationError,
)


_GLOBAL_FLAG_DEFAULTS = {"api_key": None, "base_url": None, "quiet": False, "json": False, "debug": False}


def _global_flags_parser() -> argparse.ArgumentParser:
    """Parent parser contributing the global flags to both root and subparsers,
    so they work in either position. Uses default=SUPPRESS so the absence of
    the flag at one level doesn't overwrite a value set at the other.
    """
    g = argparse.ArgumentParser(add_help=False)
    g.add_argument("--api-key", default=argparse.SUPPRESS, help="Override de SIFENDE_API_KEY (no se ecoa).")
    g.add_argument("--base-url", default=argparse.SUPPRESS, help="Override de la base URL del API.")
    g.add_argument("--quiet", "-q", action="store_true", default=argparse.SUPPRESS,
                   help="Suprimir mensajes de progreso.")
    g.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                   help="Imprimir resultados como JSON.")
    g.add_argument("--debug", action="store_true", default=argparse.SUPPRESS,
                   help="Mostrar request/response HTTP completo (API key enmascarada).")
    return g


def build_parser() -> argparse.ArgumentParser:
    globals_parser = _global_flags_parser()
    parser = argparse.ArgumentParser(
        prog="sifende",
        parents=[globals_parser],
        description="CLI para el API de facturación electrónica Sifende (Paraguay).",
    )
    parser.add_argument("--version", action="version", version=f"sifende-cli {__version__}")

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    for name, module in ALL_COMMANDS:
        module.register(subparsers, parents=[globals_parser])

    return parser


def _apply_global_defaults(args: argparse.Namespace) -> argparse.Namespace:
    """Fill in defaults for any global flag that was suppressed by argparse
    because it wasn't present in either position."""
    for k, v in _GLOBAL_FLAG_DEFAULTS.items():
        if not hasattr(args, k):
            setattr(args, k, v)
    return args


def _exit_code_for(exc: SifendeError) -> int:
    if isinstance(exc, ValidationError):
        return 4
    if isinstance(exc, ConfigError):
        return 4
    if isinstance(exc, RejectedError):
        return 2
    if isinstance(exc, PollTimeoutError):
        return 3
    if isinstance(exc, (AuthError, NotFoundError, HttpError, NetworkError)):
        return 5
    return 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _apply_global_defaults(args)

    try:
        config = load_config(api_key_override=args.api_key, base_url_override=args.base_url)
    except SifendeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return _exit_code_for(exc)

    # Find the matching command module (dest='command' is the subparser name).
    module = dict(ALL_COMMANDS).get(args.command)
    if module is None:
        parser.error(f"comando desconocido: {args.command!r}")
        return 4  # parser.error already exits, but mypy/runtime safety

    try:
        with SifendeClient(config, debug=args.debug) as client:
            return module.run(args, client)
    except KeyboardInterrupt:
        print("\ninterrumpido", file=sys.stderr)
        return 130
    except RejectedError as exc:
        # The command may have already printed the user-friendly view; here we
        # only ensure the exit code mapping. Avoid re-printing the message.
        if not getattr(args, "quiet", False):
            print(f"ERROR: {exc}", file=sys.stderr)
        return _exit_code_for(exc)
    except SifendeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return _exit_code_for(exc)


if __name__ == "__main__":
    sys.exit(main())
