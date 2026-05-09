"""`inutilizar`: void a numeric range of unused documents."""

from __future__ import annotations

import json

from ..client import SifendeClient
from ..errors import ValidationError
from ..utils.validation import validate_motivo


def register(subparsers, *, parents=()) -> None:
    p = subparsers.add_parser(
        "inutilizar",
        parents=list(parents),
        help="Inutilizar un rango de numeración no usado.",
        description="POST /documento-electronico/inutilizar.",
    )
    p.add_argument("--tipo-documento", required=True, type=int,
                   help="Código numérico iTiDe: 1=FACTURA, 5=NOTA_CREDITO, 6=NOTA_DEBITO.")
    p.add_argument("--establecimiento", required=True,
                   help="Código de establecimiento (3 dígitos, ej: 001).")
    p.add_argument("--punto-expedicion", required=True,
                   help="Código de punto de expedición (3 dígitos, ej: 001).")
    p.add_argument("--numero-timbrado", required=True,
                   help="Número de timbrado electrónico.")
    p.add_argument("--desde", required=True, type=int, help="Número inicial del rango.")
    p.add_argument("--hasta", required=True, type=int, help="Número final del rango.")
    p.add_argument("--motivo", "-m", required=True, help="Motivo de inutilización (mín. 5 caracteres).")


def run(args, client: SifendeClient) -> int:
    MAX_RANGO = 4

    motivo = validate_motivo(args.motivo)
    if args.desde < 1 or args.hasta < args.desde:
        raise ValidationError("rango", "se requiere 1 ≤ desde ≤ hasta")
    if (args.hasta - args.desde + 1) > MAX_RANGO:
        raise ValidationError("rango", f"máximo {MAX_RANGO} números por inutilización (recibido: {args.hasta - args.desde + 1})")

    est = str(args.establecimiento).zfill(3)
    pe = str(args.punto_expedicion).zfill(3)

    body = {
        "tipoDocumento": args.tipo_documento,
        "establecimiento": est,
        "puntoExpedicion": pe,
        "numeroTimbrado": args.numero_timbrado,
        "numeroInicio": str(args.desde),
        "numeroFin": str(args.hasta),
        "motivo": motivo,
    }
    payload = client.inutilizar(body)

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    elif args.quiet:
        print("OK")
    else:
        print(f"Rango inutilizado: {est}-{pe} {args.desde}..{args.hasta}")
        if isinstance(payload, dict) and payload:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
