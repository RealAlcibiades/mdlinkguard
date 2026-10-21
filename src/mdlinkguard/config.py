"""Configuration loading (.mdlinkguard.toml or [tool.mdlinkguard] in pyproject.toml)."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib


@dataclass
class Config:
    ignore: list[str] = field(default_factory=list)  # regex patterns for link targets
    exclude: list[str] = field(default_factory=list)  # glob patterns for files
    check_external: bool = False
    timeout: float = 10.0
    retries: int = 2
    concurrency: int = 8
    cache: str | None = None  # path to cache file; None disables
    cache_ttl: float = 86400.0  # seconds


def load_config(path: Path | None, root: Path) -> Config:
    data: dict = {}
    if path is not None:
        with open(path, "rb") as f:
            raw = tomllib.load(f)
        data = raw.get("tool", {}).get("mdlinkguard", raw)
    else:
        for cand in (root / ".mdlinkguard.toml", root / "pyproject.toml"):
            if cand.is_file():
                with open(cand, "rb") as f:
                    raw = tomllib.load(f)
                if cand.name == "pyproject.toml":
                    raw = raw.get("tool", {}).get("mdlinkguard")
                    if raw is None:
                        continue
                data = raw
                break
    cfg = Config()
    for key, value in data.items():
        key = key.replace("-", "_")
        if hasattr(cfg, key):
            setattr(cfg, key, value)
    return cfg
