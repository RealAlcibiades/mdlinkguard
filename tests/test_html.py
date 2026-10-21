from mdlinkguard.parser import parse


def test_html_links_and_images():
    links, _ = parse('<a href="docs/x.md">x</a> <img alt="l" src="logo.png">\n')
    assert [(l.target, l.kind) for l in links] == [("docs/x.md", "html"), ("logo.png", "image")]


def test_html_in_code_ignored():
    links, _ = parse('```\n<a href="no.md">\n```\n`<img src="no.png">`\n')
    assert links == []


def test_mdx_esm_skipped():
    text = 'import X from "./x.md"\nexport const meta = {}\n[ok](a.md)\n'
    assert [l.target for l in parse(text, mdx=True)[0]] == ["a.md"]
