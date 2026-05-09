"""`estado`: single-shot status lookup by CDC."""

from __future__ import annotations

import json
import sys

from ..client import SifendeClient
from ..errors import RejectedError
from ..models import Estado, EstadoResponse
from ..utils.validation import validate_cdc


def register(subparsers, *, parents=()) -> None:
    p = subparsers.add_parser(
        "estado",
        parents=list(parents),
        help="Consultar el estado de un documento por CDC.",
        description="Consulta una sola vez el estado del documento en SIFEN.",
    )
    p.add_argument("cdc", help="CDC de 44 dígitos.")


def run(args, client: SifendeClient) -> int:
    cdc = validate_cdc(args.cdc)
    payload = client.estado(cdc)
    resp = EstadoResponse.from_api(payload)

    if args.json:
        print(json.dumps(resp.to_dict(), ensure_ascii=False))
    elif args.quiet:
        print(resp.estado)
    else:
        print(f"CDC: {resp.cdc}")
        print(f"Estado: {resp.estado}")
        if resp.mensaje_rechazo:
            print(f"Mensaje: {resp.mensaje_rechazo}")

    if resp.estado in (Estado.RECHAZADO, Estado.ERROR):
        if args.quiet:
            print(f"{resp.estado}: {resp.mensaje_rechazo or '<sin mensaje>'}", file=sys.stderr)
        raise RejectedError(resp.cdc, resp.estado, resp.mensaje_rechazo)
    return 0
