"""`kude`: download the KuDE PDF for a given CDC, in A4 or as a paper-roll ticket."""

from __future__ import annotations

import json
import sys

from ..client import SifendeClient
from ..errors import ValidationError
from ..utils.io import save_pdf
from ..utils.validation import validate_cdc

FORMATOS = ("a4", "ticket", "ticket-resumen")


def register(subparsers, *, parents=()) -> None:
    p = subparsers.add_parser(
        "kude",
        parents=list(parents),
        help="Descargar el KuDE (PDF) de un documento.",
        description=(
            "Descarga el PDF representativo (KuDE). Con --formato ticket se genera en cinta de papel "
            "para impresoras térmicas (sólo facturas y notas de crédito o débito)."
        ),
    )
    p.add_argument("cdc", help="CDC de 44 dígitos.")
    p.add_argument(
        "--formato",
        choices=FORMATOS,
        default="a4",
        help="a4 (default), ticket o ticket-resumen (sin detalle de ítems).",
    )
    p.add_argument(
        "--ancho",
        type=int,
        choices=(80, 58),
        help="Ancho del papel del ticket en mm. Default: 80.",
    )
    p.add_argument("--out", "-o", help="Ruta destino. Default: <CDC>.pdf o <CDC>-<formato>.pdf.")


def run(args, client: SifendeClient) -> int:
    cdc = validate_cdc(args.cdc)
    formato = args.formato
    if formato == "a4":
        if args.ancho is not None:
            raise ValidationError("ancho", "sólo aplica a --formato ticket o ticket-resumen")
        out_path = args.out or f"{cdc}.pdf"
        pdf = client.kude(cdc)
    else:
        ancho = args.ancho or 80
        out_path = args.out or f"{cdc}-{formato}.pdf"
        pdf = client.kude_ticket(cdc, ancho=ancho, resumen=formato == "ticket-resumen")
    saved = save_pdf(pdf, out_path)
    bytes_written = len(pdf)

    if args.json:
        print(json.dumps({"cdc": cdc, "formato": formato, "path": saved, "bytes": bytes_written}, ensure_ascii=False))
    elif args.quiet:
        print(saved)
    else:
        print(f"KuDE guardado en: {saved} ({bytes_written} bytes)")
        print(f"CDC: {cdc}", file=sys.stderr)
    return 0
