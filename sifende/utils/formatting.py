"""Plain-text terminal formatting helpers — no color libraries."""

from __future__ import annotations

import sys
from typing import TextIO


def fmt_pyg(amount: int) -> str:
    """Render a PYG integer with thousands separators (Paraguayan style: `.`)."""
    try:
        n = int(amount)
    except (TypeError, ValueError):
        return str(amount)
    sign = "-" if n < 0 else ""
    n = abs(n)
    return f"{sign}{n:,}".replace(",", ".") + " Gs"


def write_status_line(line: str, *, stream: TextIO = sys.stderr) -> None:
    """Redraw a single live status line via carriage-return rewind.

    Pads with spaces so a shorter follow-up line erases the tail of the
    previous one. Always flushes — the loop relies on visible ticks.
    """
    if not stream.isatty():
        stream.write(line + "\n")
        stream.flush()
        return
    stream.write("\r" + line + " " * 8)
    stream.flush()


def finalize_status_line(stream: TextIO = sys.stderr) -> None:
    """Newline after the last `\\r` redraw so subsequent output starts clean."""
    if stream.isatty():
        stream.write("\n")
        stream.flush()
