"""Polling watch mode: re-run checks when Markdown files change (stdlib only)."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from .checker import _anchor_cache, find_markdown


def snapshot(paths: list[Path], exclude: list[str]) -> dict[Path, float]:
    snap = {}
    for f in find_markdown(paths, exclude):
        try:
            snap[f] = f.stat().st_mtime_ns
        except OSError:
            pass
    return snap


def watch(paths: list[Path], exclude: list[str], on_change: Callable[[], None],
          interval: float = 1.0, max_cycles: int | None = None, sleep=time.sleep) -> None:
    """Call ``on_change`` once, then again whenever a file is added, removed, or modified."""
    prev = snapshot(paths, exclude)
    on_change()
    cycles = 0
    while max_cycles is None or cycles < max_cycles:
        sleep(interval)
        cycles += 1
        cur = snapshot(paths, exclude)
        if cur != prev:
            prev = cur
            _anchor_cache.clear()
            on_change()
