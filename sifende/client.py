"""HTTP wrapper around requests. All errors flow through `errors.py`."""

from __future__ import annotations

import json as _json_mod
import sys
from typing import Optional
from urllib.parse import urljoin

import requests

from .config import Config
from .errors import (
    AuthError,
    HttpError,
    NetworkError,
    NotFoundError,
)


class SifendeClient:
    def __init__(self, config: Config, *, debug: bool = False) -> None:
        self.config = config
        self._debug = debug
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "sifende-cli/0.1",
            }
        )

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "SifendeClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _url(self, path: str) -> str:
        return urljoin(self.config.base_url, path.lstrip("/"))

    def _debug_print(self, method: str, url: str, json_body: Optional[dict], resp: Optional[requests.Response]) -> None:
        print("\n── DEBUG REQUEST ─────────────────────────────", file=sys.stderr)
        print(f"  {method} {url}", file=sys.stderr)
        # Print headers, masking the Authorization value
        for k, v in self._session.headers.items():
            if k.lower() == "authorization":
                v = v[:14] + "***" if len(v) > 14 else "***"
            print(f"  {k}: {v}", file=sys.stderr)
        if json_body is not None:
            print("  Body:", file=sys.stderr)
            print("  " + _json_mod.dumps(json_body, ensure_ascii=False, indent=2).replace("\n", "\n  "), file=sys.stderr)
        if resp is not None:
            print(f"\n── DEBUG RESPONSE ────────────────────────────", file=sys.stderr)
            print(f"  Status: {resp.status_code}", file=sys.stderr)
            for k, v in resp.headers.items():
                print(f"  {k}: {v}", file=sys.stderr)
            body = resp.text or "<empty>"
            try:
                parsed = _json_mod.loads(body)
                body = _json_mod.dumps(parsed, ensure_ascii=False, indent=2)
            except Exception:
                pass
            print("  Body:", file=sys.stderr)
            print("  " + body.replace("\n", "\n  "), file=sys.stderr)
        print("──────────────────────────────────────────────\n", file=sys.stderr)

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[dict] = None,
        accept: str = "application/json",
    ) -> requests.Response:
        url = self._url(path)
        headers = {"Accept": accept}
        try:
            resp = self._session.request(
                method,
                url,
                json=json_body,
                headers=headers,
                timeout=self.config.timeout_s,
            )
        except requests.exceptions.Timeout as exc:
            if self._debug:
                self._debug_print(method, url, json_body, None)
            raise NetworkError(f"timeout al conectar con {url}: {exc}")
        except requests.exceptions.ConnectionError as exc:
            if self._debug:
                self._debug_print(method, url, json_body, None)
            raise NetworkError(f"error de conexión con {url}: {exc}")
        except requests.exceptions.RequestException as exc:
            raise NetworkError(f"error de red: {exc}")

        if self._debug:
            self._debug_print(method, url, json_body, resp)

        if resp.status_code >= 400:
            body_text = resp.text or ""
            if resp.status_code in (401, 403):
                raise AuthError(resp.status_code, body_text, url=url)
            if resp.status_code == 404:
                raise NotFoundError(resp.status_code, body_text, url=url)
            raise HttpError(resp.status_code, body_text, url=url)

        return resp

    @staticmethod
    def _json(resp: requests.Response) -> dict:
        try:
            data = resp.json()
        except ValueError:
            raise HttpError(resp.status_code, resp.text or "<respuesta no-JSON>", url=resp.url)
        if not isinstance(data, dict):
            raise HttpError(resp.status_code, str(data), url=resp.url)
        return data

    def emitir(self, payload: dict) -> dict:
        resp = self._request("POST", "documento-electronico", json_body=payload)
        return self._json(resp)

    def estado(self, cdc: str) -> dict:
        resp = self._request("GET", f"documento-electronico/status/{cdc}")
        return self._json(resp)

    def kude(self, cdc: str) -> bytes:
        resp = self._request("GET", f"documento-electronico/{cdc}/kude", accept="application/pdf")
        return resp.content

    def cancelar(self, cdc: str, motivo: str) -> dict:
        resp = self._request(
            "POST",
            f"documento-electronico/{cdc}/cancelar",
            json_body={"motivo": motivo},
        )
        return self._json(resp)

    def inutilizar(self, body: dict) -> dict:
        resp = self._request("POST", "documento-electronico/inutilizar", json_body=body)
        return self._json(resp)
