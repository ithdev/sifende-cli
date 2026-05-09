"""`cancelar`: cancel a previously emitted document."""

from __future__ import annotations

import json

from ..client import SifendeClient
from ..utils.validation import validate_cdc, validate_motivo


def register(subparsers, *, parents=()) -> None:
    p = subparsers.add_parser(
        "cancelar",
        parents=list(parents),
        help="Cancelar un documento ya emitido.",
        description="POST /documento-electronico/:cdc/cancelar — body {motivo}.",
    )
    p.add_argument("cdc", help="CDC de 44 dígitos.")
    p.add_argument("--motivo", "-m", required=True, help="Motivo de la cancelación (mín. 5 caracteres).")


def run(args, client: SifendeClient) -> int:
    cdc = validate_cdc(args.cdc)
    motivo = validate_motivo(args.motivo)
    payload = client.cancelar(cdc, motivo)

    if args.json:
        print(json.dumps({"cdc": cdc, "result": payload}, ensure_ascii=False))
    elif args.quiet:
        print(cdc)
    else:
        print(f"CDC cancelado: {cdc}")
        if isinstance(payload, dict) and payload:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
