"""Read Telekom Glasfaser Modem 1 local status API."""

import asyncio
import json
import random
import re
import time
from urllib.parse import quote

from aiohttp import ClientError, ClientSession


class OntError(Exception):
    """ONT could not be queried."""


class OntClient:
    def __init__(self, session: ClientSession, host: str) -> None:
        self._session = session
        self.host = host
        self.base_url = f"http://{host}"
        self.overview_url = (
            f"{self.base_url}/ONT/client/html/content/overview/index.html"
        )
        self.status_url = f"{self.base_url}/ONT/client/data/Status.json"

    async def _fetch(self, url: str) -> bytes:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0",
            "Accept": "application/json, text/javascript, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-GPC": "1",
            "Referer": self.overview_url,
            "Cookie": "lang=en",
        }
        try:
            async with asyncio.timeout(10):
                async with self._session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.read()
        except (ClientError, TimeoutError, ValueError) as exc:
            raise OntError(f"ONT request failed: {exc}") from exc

    async def async_get_status(self) -> dict[str, str]:
        html = (await self._fetch(self.overview_url)).decode("iso-8859-1")
        match = re.search(r"var\s+csrf_token\s*=\s*['\"]([^'\"]+)['\"]", html)
        if not match:
            raise OntError("CSRF token not found in overview page")
        token = quote(match.group(1), safe="")
        # The device's original JavaScript intentionally produces '??'.
        url = (
            f"{self.status_url}??_time={int(time.time() * 1000)}"
            f"&_rand={random.randint(0, 1000)}&csrf_token={token}"
        )
        raw = await self._fetch(url)
        try:
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, list):
                raise ValueError("Expected JSON array")
            return {
                str(item["varid"]): str(item["varvalue"])
                for item in payload
                if isinstance(item, dict) and "varid" in item and "varvalue" in item
            }
        except (UnicodeDecodeError, ValueError, TypeError, KeyError) as exc:
            raise OntError(f"Invalid ONT status JSON: {exc}") from exc
