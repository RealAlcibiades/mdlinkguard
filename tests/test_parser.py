from mdlinkguard.parser import parse, slugify


def test_slugify():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("Use `code` here") == "use-code-here"


def test_link_kinds():
    text = """# Title
[a](b.md) ![img](pic.png "t") <https://example.com>
[ref][r] and [r]

[r]: other.md#x
"""
    links, anchors = parse(text)
    kinds = sorted(l.kind for l in links)
    assert kinds == ["autolink", "image", "inline", "reference", "reference"]
    assert "title" in anchors


def test_code_blocks_ignored():
    text = "```\n[x](missing.md)\n```\nInline `[y](z.md)` here\n"
    assert parse(text)[0] == []


def test_duplicate_headings():
    _, anchors = parse("# A\n# A\n")
    assert anchors == {"a", "a-1"}
