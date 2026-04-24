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
from typing import Any


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
