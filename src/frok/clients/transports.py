"""Concrete `Transport` implementations.

Phase 2 kept the client transport-agnostic via a Protocol so tests could
inject stubs. For Phase 3 we need *something* production-ish by default,
so the CLI can actually hit an endpoint. The stdlib-only option below
is intentionally minimal: it blocks via `urllib.request` under
`asyncio.to_thread`, so throughput is modest but dependencies stay at
zero. Swap in httpx / aiohttp behind the same Protocol when real volume
arrives.
"""

from __future__ import annotations

import asyncio
import urllib.error
import urllib.request
from typing import Any, AsyncIterator


async def urllib_transport(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    body: bytes,
    timeout: float,
) -> tuple[int, dict[str, str], bytes]:
    def _do() -> tuple[int, dict[str, str], bytes]:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return (
                    int(resp.status),
                    {k.lower(): v for k, v in resp.headers.items()},
                    resp.read(),
                )
        except urllib.error.HTTPError as err:
            return (
                int(err.code),
                {k.lower(): v for k, v in (err.headers or {}).items()},
                err.read() or b"",
            )

    return await asyncio.to_thread(_do)


async def urllib_streaming_transport(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    body: bytes,
    timeout: float,
) -> tuple[int, dict[str, str], AsyncIterator[bytes]]:
    """Stdlib streaming transport built on `urllib.request.urlopen`.

    Reads line-by-line via ``asyncio.to_thread`` so the event loop isn't
    blocked, but each readline is a thread hop — low-throughput compared
    to httpx/aiohttp. Adequate for the CLI's live-progress display;
    swap in a real async HTTP client behind `StreamingTransport` when
    production volume arrives.

    On a 4xx / 5xx, returns the status + a one-shot body iterator so
    `GrokClient.chat_stream` can surface a meaningful `HttpError`.
    """

    def _open() -> urllib.request.addinfourl:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        return urllib.request.urlopen(req, timeout=timeout)

    try:
        resp = await asyncio.to_thread(_open)
    except urllib.error.HTTPError as err:
        status = int(err.code)
        hdrs = {k.lower(): v for k, v in (err.headers or {}).items()}
        err_body = err.read() or b""

        async def _error_iter() -> AsyncIterator[bytes]:
            yield err_body

        return status, hdrs, _error_iter()

    status = int(resp.status)
    hdrs = {k.lower(): v for k, v in resp.headers.items()}

    async def _iter() -> AsyncIterator[bytes]:
        try:
            while True:
                line: bytes = await asyncio.to_thread(resp.readline)
                if not line:
                    break
                yield line
        finally:
            resp.close()

    return status, hdrs, _iter()
