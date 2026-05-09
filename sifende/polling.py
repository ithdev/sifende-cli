"""Status polling loop for `emitir`.

Live single-line ticker via `\\r` redraws. State transitions print a newline
so the history of EN_LOTE → ENVIADO → APROBADO stays visible after the run.
"""

from __future__ import annotations

import sys
import time
from typing import Optional

from .client import SifendeClient
from .errors import HttpError, NetworkError, TimeoutError as PollTimeoutError
from .models import EstadoResponse, TERMINAL_ESTADOS
from .utils.formatting import finalize_status_line, write_status_line


DEFAULT_INTERVAL_S = 3.0
DEFAULT_TIMEOUT_S = 120.0
MAX_NETWORK_RETRIES = 3


def poll_until_terminal(
    client: SifendeClient,
    cdc: str,
    *,
    interval_s: float = DEFAULT_INTERVAL_S,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    quiet: bool = False,
    initial_estado: Optional[str] = None,
) -> EstadoResponse:
    """Poll status until terminal or timeout. Returns the final EstadoResponse.

    Raises:
        TimeoutError: deadline exceeded without reaching a terminal state.
        HttpError / NetworkError: surfaced after MAX_NETWORK_RETRIES on network errors.
    """
    start = time.monotonic()
    deadline = start + timeout_s
    attempt = 0
    last_estado = initial_estado or "PENDIENTE"
    network_failures = 0

    if not quiet:
        write_status_line(f"[00] estado={last_estado} (esperando...)")

    while time.monotonic() < deadline:
        attempt += 1
        try:
            payload = client.estado(cdc)
            network_failures = 0
        except NetworkError as exc:
            network_failures += 1
            if not quiet:
                write_status_line(
                    f"[{attempt:02d}] red caída ({network_failures}/{MAX_NETWORK_RETRIES})"
                )
            if network_failures >= MAX_NETWORK_RETRIES:
                if not quiet:
                    finalize_status_line()
                    print(f"CDC={cdc}", file=sys.stderr)
                raise
            time.sleep(interval_s)
            continue
        except HttpError:
            if not quiet:
                finalize_status_line()
                print(f"CDC={cdc}", file=sys.stderr)
            raise

        resp = EstadoResponse.from_api(payload)
        elapsed = time.monotonic() - start

        if resp.estado != last_estado:
            if not quiet:
                # Newline so the previous state is preserved in scrollback,
                # then start a fresh live line for the new state.
                finalize_status_line()
            last_estado = resp.estado

        if not quiet:
            write_status_line(
                f"[{attempt:02d}] estado={resp.estado} elapsed={elapsed:0.0f}s"
            )

        if resp.estado in TERMINAL_ESTADOS:
            if not quiet:
                finalize_status_line()
            return resp

        time.sleep(interval_s)

    if not quiet:
        finalize_status_line()
    raise PollTimeoutError(cdc, last_estado, time.monotonic() - start)
