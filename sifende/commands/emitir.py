"""`emitir`: send an invoice and (optionally) poll until terminal."""

from __future__ import annotations

import json
import sys

from ..client import SifendeClient
from ..errors import RejectedError, TimeoutError as PollTimeoutError
from ..interactive import build_factura_interactive
from ..models import Estado, EmitirResponse
from ..polling import DEFAULT_TIMEOUT_S, poll_until_terminal
from ..utils.io import load_json_payload, save_document_folder, save_pdf
from ..utils.validation import validate_factura_payload


def register(subparsers, *, parents=()) -> None:
    p = subparsers.add_parser(
        "emitir",
        parents=list(parents),
        help="Emitir un documento electrónico (FACTURA, NC, ND).",
        description="Envía un documento electrónico a Sifende y, por defecto, "
        "espera a que llegue a un estado terminal (APROBADO/RECHAZADO/ERROR).",
    )
    p.add_argument("--file", "-f", help="Ruta a un JSON con el payload (omitir = modo interactivo).")
    p.add_argument("--no-wait", action="store_true", help="Devolver el CDC sin esperar el estado final.")
    p.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_S,
        help=f"Tiempo máximo de polling en segundos (default: {DEFAULT_TIMEOUT_S:.0f}).",
    )
    p.add_argument("--save-pdf", help="Si APROBADO, guardar el KuDE en esta ruta.")


def run(args, client: SifendeClient) -> int:
    if args.file:
        payload = load_json_payload(args.file)
    else:
        try:
            payload = build_factura_interactive()
        except KeyboardInterrupt:
            print("\nemisión cancelada", file=sys.stderr)
            return 130

    validate_factura_payload(payload)

    response_payload = client.emitir(payload)
    initial = EmitirResponse.from_api(response_payload)

    if not initial.cdc:
        print("ERROR: la respuesta no incluyó CDC", file=sys.stderr)
        if not args.quiet:
            print(json.dumps(response_payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 5

    if args.no_wait:
        if args.json:
            print(json.dumps(initial.to_dict(), ensure_ascii=False))
        elif args.quiet:
            print(initial.cdc)
        else:
            print(f"CDC: {initial.cdc}")
            print(f"Estado: {initial.estado}")
            print("(--no-wait: no se hizo polling)")
        return 0

    if not args.quiet:
        print(f"CDC: {initial.cdc}")
        print(f"Estado inicial: {initial.estado}")

    try:
        final = poll_until_terminal(
            client,
            initial.cdc,
            timeout_s=args.timeout,
            quiet=args.quiet,
            initial_estado=initial.estado,
        )
    except KeyboardInterrupt:
        print(f"\npolling interrumpido. CDC={initial.cdc}", file=sys.stderr)
        print(f"Reanudá con: sifende estado {initial.cdc}", file=sys.stderr)
        return 130
    except PollTimeoutError as exc:
        print(f"TIMEOUT: {exc}", file=sys.stderr)
        print(f"Reanudá con: sifende estado {exc.cdc}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps(final.to_dict(), ensure_ascii=False))
    elif not args.quiet:
        print(f"\nResultado: {final.estado}")
        if final.mensaje_rechazo:
            print(f"Mensaje SIFEN: {final.mensaje_rechazo}")

    approved = final.estado in (Estado.APROBADO, Estado.APROBADO_OBSERVACION)

    if not approved:
        if args.quiet:
            print(f"{final.estado}: {final.mensaje_rechazo or '<sin mensaje>'}", file=sys.stderr)
        raise RejectedError(final.cdc, final.estado, final.mensaje_rechazo)

    # Always save to documentos/{cdc}/ on approval.
    pdf = client.kude(final.cdc)
    folder = save_document_folder(final.cdc, payload, final.raw, pdf)
    if not args.quiet:
        print(f"Guardado en: {folder}/")

    # --save-pdf: additional copy at a user-specified path.
    if args.save_pdf:
        save_pdf(pdf, args.save_pdf)
        if not args.quiet:
            print(f"KuDE también en: {args.save_pdf}")

    if args.quiet:
        print(final.cdc)
    return 0
