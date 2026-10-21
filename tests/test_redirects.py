from mdlinkguard.checker import run
from mdlinkguard.config import Config


def _setup(tmp_path):
    (tmp_path / "a.md").write_text("[w](http://example.com/old)\n[s](https://example.com/same/)\n")
    def fetch(u, t):
        return (200, "https://example.com/new") if u.endswith("old") else (200, "https://example.com/same")
    return fetch


def test_redirect_reported(tmp_path):
    res = run([tmp_path], Config(check_external=True), _setup(tmp_path))
    by = {r.target: r for r in res}
    assert by["http://example.com/old"].ok and by["http://example.com/old"].redirect == "https://example.com/new"
    assert by["https://example.com/same/"].redirect == ""


def test_fail_on_redirect(tmp_path):
    res = run([tmp_path], Config(check_external=True, fail_on_redirect=True), _setup(tmp_path))
    assert [r.reason for r in res if not r.ok] == ["redirects to https://example.com/new"]
