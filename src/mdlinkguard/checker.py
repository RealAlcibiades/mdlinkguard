"""Link checking logic."""
from __future__ import annotations

import difflib
import fnmatch
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import unquote, urlsplit

from .cache import UrlCache
from .config import Config
from .ratelimit import HostRateLimiter
from .parser import Link, parse

MD_SUFFIXES = {".md", ".markdown", ".mdx"}
SKIP_SCHEMES = {"mailto", "tel", "ftp", "data", "javascript"}


@dataclass
class Result:
    file: str
    line: int
    target: str
    kind: str
    ok: bool
    reason: str = ""
    redirect: str = ""  # final URL when an external link redirects

    def to_dict(self) -> dict:
        return asdict(self)


def find_markdown(paths: list[Path], exclude: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files.extend(f for f in sorted(p.rglob("*")) if f.suffix.lower() in MD_SUFFIXES and f.is_file())
        elif p.is_file():
            files.append(p)
    def excluded(f: Path) -> bool:
        s = f.as_posix()
        return any(fnmatch.fnmatch(s, pat) or fnmatch.fnmatch(f.name, pat) for pat in exclude)
    seen, out = set(), []
    for f in files:
        if f.resolve() not in seen and not excluded(f):
            seen.add(f.resolve())
            out.append(f)
    return out


_anchor_cache: dict[Path, set[str]] = {}


def anchors_for(path: Path) -> set[str]:
    key = path.resolve()
    if key not in _anchor_cache:
        _anchor_cache[key] = parse(path.read_text(encoding="utf-8", errors="replace"))[1]
    return _anchor_cache[key]


def suggest(frag: str, anchors: set[str]) -> str:
    """Return ' (did you mean #x?)' for the closest existing anchor, or ''."""
    best = difflib.get_close_matches(frag.lower(), sorted(anchors), n=1, cutoff=0.6)
    return f"; did you mean #{best[0]}?" if best else ""


def check_local(src: Path, target: str, own_anchors: set[str]) -> str:
    """Return '' if ok, else a reason string."""
    path_part, _, frag = target.partition("#")
    frag = unquote(frag)
    if not path_part:
        return "" if frag in own_anchors or frag.lower() in own_anchors else f"missing anchor #{frag}" + suggest(frag, own_anchors)
    rel = unquote(path_part.split("?")[0])
    dest = (src.parent / rel) if not rel.startswith("/") else Path(rel)
    if not dest.exists():
        return "file not found"
    if frag and dest.is_file() and dest.suffix.lower() in MD_SUFFIXES:
        if frag not in anchors_for(dest) and frag.lower() not in anchors_for(dest):
            return f"missing anchor #{frag}" + suggest(frag, anchors_for(dest))
    return ""


Fetcher = Callable[[str, float], "int | tuple[int, str]"]


def http_status(url: str, timeout: float) -> int:
    headers = {"User-Agent": "mdlinkguard/0.5.0 (+https://github.com/RealAlcibiades/mdlinkguard)"}
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.geturl()
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue
            return e.code
    return 0  # pragma: no cover


def check_url(url: str, cfg: Config, fetch: Fetcher = http_status) -> str:
    return check_url_full(url, cfg, fetch)[0]


def check_url_full(url: str, cfg: Config, fetch: Fetcher = http_status,
                   limiter: HostRateLimiter | None = None) -> tuple[str, str]:
    """Return (reason, final_url). reason is '' when the URL works."""
    last = ""
    for attempt in range(cfg.retries + 1):
        try:
            if limiter:
                limiter.wait(url)
            got = fetch(url, cfg.timeout)
            code, final = got if isinstance(got, tuple) else (got, url)
            if 200 <= code < 400:
                return "", ("" if final.rstrip("/") == url.rstrip("/") else final)
            last = f"HTTP {code}"
            if code not in (429,) and code < 500:
                return last, ""
        except Exception as e:  # network errors, timeouts
            last = f"{type(e).__name__}: {e}"
        if attempt < cfg.retries:
            time.sleep(min(0.5 * 2**attempt, 4))
    return last, ""


def run(paths: list[Path], cfg: Config, fetch: Fetcher = http_status) -> list[Result]:
    ignore = [re.compile(p) for p in cfg.ignore]
    results: list[Result] = []
    pending: list[tuple[int, str]] = []
    for f in find_markdown(paths, cfg.exclude):
        links, anchors = parse(f.read_text(encoding="utf-8", errors="replace"), mdx=f.suffix.lower() == ".mdx")
        _anchor_cache[f.resolve()] = anchors
        for link in links:
            t = link.target
            if not t or any(r.search(t) for r in ignore):
                continue
            scheme = urlsplit(t).scheme.lower()
            res = Result(str(f), link.line, t, link.kind, True)
            if scheme in ("http", "https"):
                if not cfg.check_external:
                    continue
                pending.append((len(results), t))
            elif scheme in SKIP_SCHEMES or (scheme and len(scheme) > 1):
                continue
            else:
                reason = check_local(f, t, anchors)
                res.ok, res.reason = not reason, reason
            results.append(res)
    if pending:
        cache = UrlCache(Path(cfg.cache) if cfg.cache else None, cfg.cache_ttl)
        unique = sorted({u for _, u in pending})
        outcome: dict[str, tuple[str, str]] = {}
        todo = []
        for u in unique:
            hit = cache.get(u)
            if hit is None:
                todo.append(u)
            else:
                outcome[u] = (hit, "")
        limiter = HostRateLimiter(cfg.rate_limit, cfg.host_rate_limits)
        with ThreadPoolExecutor(max_workers=max(1, cfg.concurrency)) as ex:
            for u, res in zip(todo, ex.map(lambda u: check_url_full(u, cfg, fetch, limiter), todo)):
                outcome[u] = res
                if not res[1]:
                    cache.put(u, res[0])
        cache.save()
        for idx, url in pending:
            reason, final = outcome[url]
            results[idx].ok = not reason
            results[idx].reason = reason
            results[idx].redirect = final
            if final and cfg.fail_on_redirect:
                results[idx].ok = False
                results[idx].reason = f"redirects to {final}"
    return results
