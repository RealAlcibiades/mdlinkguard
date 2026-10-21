"""Command-line interface."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .checker import run
from .config import load_config


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mdlinkguard", description="Find broken links in Markdown files.")
    p.add_argument("paths", nargs="*", default=["."], help="files or directories (default: .)")
    p.add_argument("-e", "--external", action="store_true", help="also check http(s) URLs")
    p.add_argument("-i", "--ignore", action="append", default=[], metavar="REGEX", help="ignore link targets matching REGEX (repeatable)")
    p.add_argument("-x", "--exclude", action="append", default=[], metavar="GLOB", help="skip files matching GLOB (repeatable)")
    p.add_argument("-c", "--config", type=Path, help="path to a TOML config file")
    p.add_argument("--timeout", type=float, help="HTTP timeout in seconds")
    p.add_argument("--retries", type=int, help="HTTP retries for transient errors")
    p.add_argument("-j", "--concurrency", type=int, help="parallel HTTP requests")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("-v", "--verbose", action="store_true", help="also list working links")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config(args.config, Path.cwd())
    cfg.ignore = list(cfg.ignore) + args.ignore
    cfg.exclude = list(cfg.exclude) + args.exclude
    if args.external:
        cfg.check_external = True
    for name in ("timeout", "retries", "concurrency"):
        if getattr(args, name) is not None:
            setattr(cfg, name, getattr(args, name))
    paths = [Path(p) for p in args.paths]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"mdlinkguard: path not found: {missing[0]}", file=sys.stderr)
        return 2
    results = run(paths, cfg)
    broken = [r for r in results if not r.ok]
    if args.format == "json":
        json.dump({"checked": len(results), "broken": len(broken),
                   "results": [r.to_dict() for r in (results if args.verbose else broken)]}, sys.stdout, indent=2)
        print()
    else:
        for r in results:
            if not r.ok:
                print(f"{r.file}:{r.line}: BROKEN {r.target} ({r.reason})")
            elif args.verbose:
                print(f"{r.file}:{r.line}: ok {r.target}")
        print(f"{len(results)} links checked, {len(broken)} broken.")
    return 1 if broken else 0
