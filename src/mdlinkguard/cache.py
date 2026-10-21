"""On-disk cache of external URL results with a time-to-live."""
from __future__ import annotations

import json
import time
from pathlib import Path


class UrlCache:
    def __init__(self, path: Path | None, ttl: float = 86400.0):
        self.path, self.ttl = path, ttl
        self.data: dict[str, dict] = {}
        if path and path.is_file():
            try:
                self.data = json.loads(path.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                self.data = {}

    def get(self, url: str) -> str | None:
        entry = self.data.get(url)
        if entry is None or time.time() - entry.get("ts", 0) > self.ttl:
            return None
        return entry.get("reason", "")

    def put(self, url: str, reason: str) -> None:
        # Only cache successes; failures should be re-checked next run.
        if reason == "":
            self.data[url] = {"reason": "", "ts": time.time()}

    def save(self) -> None:
        if self.path:
            self.path.write_text(json.dumps(self.data, indent=1, sort_keys=True), encoding="utf-8")
