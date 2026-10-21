"""Per-host rate limiting so large docs sites don't hammer a single server."""
from __future__ import annotations

import threading
import time
from urllib.parse import urlsplit


class HostRateLimiter:
    """Enforce a minimum interval between requests to the same host.

    ``default`` is requests per second for any host (0 = unlimited);
    ``per_host`` overrides it, e.g. ``{"github.com": 2}``. Subdomains match
    their parent entry (``api.github.com`` uses ``github.com``).
    """

    def __init__(self, default: float = 0.0, per_host: dict[str, float] | None = None,
                 clock=time.monotonic, sleep=time.sleep):
        self.default, self.per_host = default, dict(per_host or {})
        self.clock, self.sleep = clock, sleep
        self._next: dict[str, float] = {}
        self._lock = threading.Lock()

    def rate_for(self, host: str) -> float:
        parts = host.split(".")
        for i in range(len(parts) - 1):
            cand = ".".join(parts[i:])
            if cand in self.per_host:
                return self.per_host[cand]
        return self.default

    def wait(self, url: str) -> None:
        host = (urlsplit(url).hostname or "").lower()
        rate = self.rate_for(host)
        if rate <= 0:
            return
        with self._lock:
            now = self.clock()
            start = max(now, self._next.get(host, now))
            self._next[host] = start + 1.0 / rate
        if start > now:
            self.sleep(start - now)
