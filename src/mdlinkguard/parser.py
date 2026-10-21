"""Extract links and headings from Markdown text."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")
INLINE_RE = re.compile(r"(!?)\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*<?([^)\s>]*)>?(?:\s+[\"'(].*?[\"')])?\s*\)")
REF_USE_RE = re.compile(r"(!?)\[([^\]]+)\](?:\[([^\]]*)\])?(?![(:])")
REF_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*<?(\S+?)>?(?:\s+.*)?$")
AUTOLINK_RE = re.compile(r"<((?:https?|ftp)://[^>\s]+|mailto:[^>\s]+)>")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
HTML_LINK_RE = re.compile(r"""<(a|img)\b[^>]*?\s(href|src)\s*=\s*["']([^"']+)["']""", re.I)
MDX_ESM_RE = re.compile(r"^(import|export)\s")
HTML_ANCHOR_RE = re.compile(r"""<a\s+[^>]*(?:name|id)=["']([^"']+)["']""", re.I)


@dataclass(frozen=True)
class Link:
    target: str
    line: int
    kind: str  # inline | image | reference | autolink | html


def slugify(text: str) -> str:
    """GitHub-style heading slug."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("`", "").strip().lower()
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        if ch in "-_ " or cat[0] in "LN":
            out.append("-" if ch == " " else ch)
    return "".join(out)


def _strip_code(lines: list[str]) -> list[str]:
    result, fence = [], None
    for line in lines:
        m = FENCE_RE.match(line)
        if fence:
            if m and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence):
                fence = None
            result.append("")
            continue
        if m:
            fence = m.group(2)
            result.append("")
            continue
        result.append(INLINE_CODE_RE.sub(lambda x: " " * len(x.group(0)), line))
    return result


def parse(text: str, mdx: bool = False) -> tuple[list[Link], set[str]]:
    """Return (links, anchors) for a Markdown document.

    With ``mdx=True``, top-level ``import``/``export`` statements are ignored.
    """
    lines = _strip_code(text.splitlines())
    if mdx:
        lines = ["" if MDX_ESM_RE.match(l) else l for l in lines]
    defs: dict[str, tuple[str, int]] = {}
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    links: list[Link] = []
    for i, line in enumerate(lines, 1):
        d = REF_DEF_RE.match(line)
        if d:
            defs[d.group(1).strip().lower()] = (d.group(2), i)
            continue
        h = HEADING_RE.match(line)
        if h:
            slug = slugify(h.group(2))
            n = counts.get(slug, 0)
            counts[slug] = n + 1
            anchors.add(slug if n == 0 else f"{slug}-{n}")
        for a in HTML_ANCHOR_RE.finditer(line):
            anchors.add(a.group(1))
        for m in INLINE_RE.finditer(line):
            links.append(Link(m.group(3), i, "image" if m.group(1) else "inline"))
        for m in HTML_LINK_RE.finditer(line):
            links.append(Link(m.group(3), i, "image" if m.group(1).lower() == "img" else "html"))
        for m in AUTOLINK_RE.finditer(line):
            links.append(Link(m.group(1), i, "autolink"))
    for i, line in enumerate(lines, 1):
        if REF_DEF_RE.match(line):
            continue
        cleaned = INLINE_RE.sub("", line)
        for m in REF_USE_RE.finditer(cleaned):
            label = (m.group(3) or m.group(2)).strip().lower()
            if label in defs:
                links.append(Link(defs[label][0], i, "image" if m.group(1) else "reference"))
    links.sort(key=lambda l: l.line)
    return links, anchors
