from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from .errors import RelivioApiError, RelivioNetworkError, RelivioTimeoutError
from .types.options import ResolvedOptions

try:
    import httpx
except ModuleNotFoundError:  # pragma: no cover - runtime dependency check
    httpx = None  # type: ignore[assignment]


class HttpTransport:
    def __init__(self, config: ResolvedOptions):
        self._config = config
        self._sync_client = self._build_sync_client()
        self._async_client = self._build_async_client()

    def _build_sync_client(self):
        _require_httpx()
        return httpx.Client(  # type: ignore[union-attr]
            base_url=self._config.base_url,
            headers=_base_headers(self._config.api_key),
            timeout=self._config.timeout_s,
        )

    def _build_async_client(self):
        _require_httpx()
        return httpx.AsyncClient(  # type: ignore[union-attr]
            base_url=self._config.base_url,
            headers=_base_headers(self._config.api_key),
            timeout=self._config.timeout_s,
        )

    def request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        return self._request_with_retry(
            client=self._sync_client,
            method=method,
            path=path,
            body=body,
            idempotency_key=idempotency_key,
            params=params,
        )

    async def arequest(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        params: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        return await self._arequest_with_retry(
            client=self._async_client,
            method=method,
            path=path,
            body=body,
            idempotency_key=idempotency_key,
            params=params,
        )

    def _request_with_retry(
        self,
        *,
        client,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]],
        idempotency_key: Optional[str],
        params: Optional[Dict[str, str]],
    ) -> Dict[str, Any]:
        attempts = self._config.max_retries + 1
        request_path = _request_path(path, params)
        for attempt in range(attempts):
            try:
                response = client.request(
                    method=method,
                    url=request_path,
                    json=body,
                    headers=_request_headers(idempotency_key),
                )
            except Exception as exc:  # pragma: no cover - thin mapping
                raise _map_httpx_error(exc, self._config.timeout_s) from exc

            if response.status_code == 429 and attempt < self._config.max_retries:
                time.sleep(_retry_delay_seconds(response))
                continue

            return _parse_response(response)

        raise AssertionError("unreachable")

    async def _arequest_with_retry(
        self,
        *,
        client,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]],
        idempotency_key: Optional[str],
        params: Optional[Dict[str, str]],
    ) -> Dict[str, Any]:
        attempts = self._config.max_retries + 1
        request_path = _request_path(path, params)
        for attempt in range(attempts):
            try:
                response = await client.request(
                    method=method,
                    url=request_path,
                    json=body,
                    headers=_request_headers(idempotency_key),
                )
            except Exception as exc:  # pragma: no cover - thin mapping
                raise _map_httpx_error(exc, self._config.timeout_s) from exc

            if response.status_code == 429 and attempt < self._config.max_retries:
                await asyncio.sleep(_retry_delay_seconds(response))
                continue

            return _parse_response(response)

        raise AssertionError("unreachable")


def _require_httpx() -> None:
    if httpx is None:
        raise ModuleNotFoundError(
            "httpx is required. Install relivio with its runtime dependencies."
        )


def _base_headers(api_key: str) -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }


def _request_headers(idempotency_key: Optional[str]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def _request_path(path: str, params: Optional[Dict[str, str]]) -> str:
    if not params:
        return path
    return f"{path}?{urlencode(params)}"


def _retry_delay_seconds(response) -> float:
    raw = response.headers.get("Retry-After")
    try:
        parsed = float(raw) if raw is not None else 1.0
    except ValueError:
        parsed = 1.0
    return max(0.0, min(parsed, 30.0))


def _parse_response(response) -> dict[str, Any]:
    text = response.text
    payload = _parse_json_body(text)

    if 200 <= response.status_code < 300:
        if isinstance(payload, dict):
            return payload
        raise RelivioApiError(
            "Relivio API returned an invalid JSON payload.",
            response.status_code,
            "INVALID_RESPONSE",
            None,
        )

    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, dict):
        message = error.get("message")
        code = error.get("code")
        request_id = error.get("request_id")
        raise RelivioApiError(
            message if isinstance(message, str) else "Relivio API request failed.",
            response.status_code,
            code if isinstance(code, str) else "UNKNOWN_ERROR",
            request_id if isinstance(request_id, str) else None,
        )

    raise RelivioApiError(
        f"Relivio API request failed with status {response.status_code}.",
        response.status_code,
        "UNKNOWN_ERROR",
        None,
    )


def _parse_json_body(text: str) -> Any:
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RelivioApiError(
            "Relivio API returned invalid JSON.",
            502,
            "INVALID_RESPONSE",
            None,
        ) from exc


def _map_httpx_error(exc: Exception, timeout_s: float):
    if httpx is not None:  # pragma: no branch
        if isinstance(exc, httpx.TimeoutException):  # type: ignore[union-attr]
            return RelivioTimeoutError(timeout_s)
        if isinstance(exc, httpx.HTTPError):  # type: ignore[union-attr]
            return RelivioNetworkError(exc)
    return RelivioNetworkError(exc)
