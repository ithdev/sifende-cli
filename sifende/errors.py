"""Typed error hierarchy for the Sifende CLI.

All user-visible error paths funnel through these classes. Importantly,
none of them ever embed the API key in their string form; HttpError
explicitly redacts request headers so an exception traceback in a CI log
can never leak a Bearer token.
"""

from __future__ import annotations

from typing import Optional


class SifendeError(Exception):
    """Base class for every error raised by the CLI."""


class ConfigError(SifendeError):
    """Missing API key, malformed base URL, unreadable .env, etc."""


class ValidationError(SifendeError):
    """Local validation failure — never reached the network."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")
        self.field = field
        self.message = message


class NetworkError(SifendeError):
    """Wraps requests.RequestException (timeouts, DNS, refused, etc.)."""


class HttpError(SifendeError):
    """Non-2xx HTTP response from Sifende.

    `body` is the raw response body (truncated to keep tracebacks small).
    The Authorization header is intentionally never stored or rendered.
    """

    BODY_PREVIEW_CHARS = 800

    def __init__(self, status: int, body: str, *, url: Optional[str] = None) -> None:
        self.status = status
        self.body = (body or "")[: self.BODY_PREVIEW_CHARS]
        self.url = url
        super().__init__(self._format())

    def _format(self) -> str:
        path = ""
        if self.url:
            try:
                from urllib.parse import urlsplit
                path = urlsplit(self.url).path or ""
            except Exception:
                path = ""
        suffix = f" {path}" if path else ""
        body = self.body.strip() or "<empty>"
        return f"HTTP {self.status}{suffix}: {body}"

    def __str__(self) -> str:
        return self._format()


class AuthError(HttpError):
    """401 / 403 — bad or missing API key."""


class NotFoundError(HttpError):
    """404 — CDC or resource does not exist."""


class RejectedError(SifendeError):
    """SIFEN returned a terminal RECHAZADO or ERROR state.

    `cdc` is preserved for document operations. Event operations such as
    inutilizacion do not have a CDC, so they pass ``None``.
    `mensaje_rechazo` is verbatim from SIFEN and printed unchanged.
    """

    def __init__(self, cdc: Optional[str], estado: str, mensaje_rechazo: Optional[str]) -> None:
        self.cdc = cdc
        self.estado = estado
        self.mensaje_rechazo = mensaje_rechazo or ""
        reference = f" (CDC={cdc})" if cdc else ""
        super().__init__(f"{estado}{reference}: {self.mensaje_rechazo or '<sin mensaje>'}")


class TimeoutError(SifendeError):  # noqa: A001 — intentional shadow, scoped to this module's namespace
    """Polling exceeded the deadline before reaching a terminal state."""

    def __init__(self, cdc: str, last_estado: str, elapsed_s: float) -> None:
        self.cdc = cdc
        self.last_estado = last_estado
        self.elapsed_s = elapsed_s
        super().__init__(
            f"timeout after {elapsed_s:.0f}s (CDC={cdc}, último estado={last_estado})"
        )
