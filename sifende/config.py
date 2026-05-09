"""Config loader: precedence is CLI flag > env > .env in CWD > .env in package root.

We deliberately do not log which file the key came from — that would leak
the path of a credential file in CI output.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .errors import ConfigError


DEFAULT_BASE_URL = "https://api.sifende.com.py/api/v1/"
DEFAULT_TIMEOUT_S = 30.0


@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    timeout_s: float = DEFAULT_TIMEOUT_S


def _parse_dotenv(path: Path) -> dict:
    """Minimal KEY=VALUE parser. No interpolation, no exports, no quoting tricks
    beyond stripping a single matched pair of surrounding quotes.
    """
    if not path.is_file():
        return {}
    out: dict = {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "=" not in stripped:
                    continue
                key, _, value = stripped.partition("=")
                key = key.strip()
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                if key:
                    out[key] = value
    except OSError:
        # Treat unreadable .env as absent — never echo the path in errors.
        return {}
    return out


def _package_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_config(
    *,
    api_key_override: Optional[str] = None,
    base_url_override: Optional[str] = None,
) -> Config:
    """Resolve the active configuration. CLI flags win; otherwise env > .env files."""
    cwd_env = _parse_dotenv(Path.cwd() / ".env")
    pkg_env = _parse_dotenv(_package_root() / ".env")

    def _resolve(name: str, override: Optional[str], default: Optional[str]) -> Optional[str]:
        if override is not None:
            return override
        v = os.environ.get(name)
        if v:
            return v
        v = cwd_env.get(name)
        if v:
            return v
        v = pkg_env.get(name)
        if v:
            return v
        return default

    api_key = _resolve("SIFENDE_API_KEY", api_key_override, None)
    if not api_key:
        raise ConfigError(
            "SIFENDE_API_KEY no configurada. "
            "Definila como variable de entorno, en .env, o pasala con --api-key."
        )

    base_url = _resolve("SIFENDE_BASE_URL", base_url_override, DEFAULT_BASE_URL) or DEFAULT_BASE_URL
    if not base_url.startswith(("http://", "https://")):
        raise ConfigError(f"base URL inválida: {base_url!r}")
    if not base_url.endswith("/"):
        base_url = base_url + "/"

    timeout_raw = _resolve("SIFENDE_TIMEOUT_S", None, str(DEFAULT_TIMEOUT_S))
    try:
        timeout_s = float(timeout_raw) if timeout_raw is not None else DEFAULT_TIMEOUT_S
    except ValueError:
        timeout_s = DEFAULT_TIMEOUT_S

    return Config(api_key=api_key, base_url=base_url, timeout_s=timeout_s)
