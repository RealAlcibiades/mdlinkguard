"""Output formats: GitHub Actions annotations and SARIF 2.1.0."""
from __future__ import annotations

import json
from pathlib import Path

from . import __version__
from .checker import Result


def _esc(s: str) -> str:
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def github(results: list[Result]) -> str:
    """Workflow commands that GitHub renders as inline PR annotations."""
    lines = []
    for r in results:
        if not r.ok:
            f = _esc(r.file).replace(",", "%2C").replace(":", "%3A")
            lines.append(f"::error file={f},line={r.line},title=Broken link::{_esc(r.target)} ({_esc(r.reason)})")
    return "\n".join(lines)


def sarif(results: list[Result]) -> str:
    out = []
    for r in results:
        if r.ok:
            continue
        out.append({
            "ruleId": "broken-link",
            "level": "error",
            "message": {"text": f"Broken link {r.target}: {r.reason}"},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": Path(r.file).as_posix()},
                "region": {"startLine": r.line},
            }}],
        })
    doc = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "mdlinkguard", "version": __version__,
                "informationUri": "https://github.com/RealAlcibiades/mdlinkguard",
                "rules": [{"id": "broken-link", "shortDescription": {"text": "Link target is unreachable or missing"}}],
            }},
            "results": out,
        }],
    }
    return json.dumps(doc, indent=2)


def stats(results: list[Result]) -> str:
    """Human-readable summary: totals by link kind, broken by reason and by file."""
    from collections import Counter
    kinds = Counter(r.kind for r in results)
    broken = [r for r in results if not r.ok]
    reasons = Counter(r.reason.split(";")[0] for r in broken)
    files = Counter(r.file for r in broken)
    files_total = len({r.file for r in results})
    out = [f"Summary: {len(results)} links in {files_total} files, {len(broken)} broken"]
    out.append("  by kind: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    if broken:
        out.append("  top reasons:")
        out += [f"    {n:>4}  {r}" for r, n in reasons.most_common(5)]
        out.append("  worst files:")
        out += [f"    {n:>4}  {f}" for f, n in files.most_common(5)]
    return "\n".join(out)
