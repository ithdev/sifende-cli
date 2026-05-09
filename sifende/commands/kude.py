"""`kude`: download the KuDE PDF for a given CDC."""

from __future__ import annotations

import json
import sys

from ..client import SifendeClient
from ..utils.io import save_pdf
from ..utils.validation import validate_cdc


def register(subparsers, *, parents=()) -> None:
    p = subparsers.add_parser(
        "kude",
        parents=list(parents),
        help="Descargar el KuDE (PDF) de un documento.",
        description="Descarga el PDF representativo (KuDE) generado por SIFEN.",
    )
    p.add_argument("cdc", help="CDC de 44 dígitos.")
    p.add_argument("--out", "-o", help="Ruta destino. Default: <CDC>.pdf en el directorio actual.")


def run(args, client: SifendeClient) -> int:
    cdc = validate_cdc(args.cdc)
    out_path = args.out or f"{cdc}.pdf"
    pdf = client.kude(cdc)
    saved = save_pdf(pdf, out_path)
    bytes_written = len(pdf)

    if args.json:
        print(json.dumps({"cdc": cdc, "path": saved, "bytes": bytes_written}, ensure_ascii=False))
    elif args.quiet:
        print(saved)
    else:
        print(f"KuDE guardado en: {saved} ({bytes_written} bytes)")
        print(f"CDC: {cdc}", file=sys.stderr)
    return 0
