from mdlinkguard.checker import run, suggest
from mdlinkguard.config import Config


def test_suggest_close_heading():
    assert suggest("instalation", {"installation", "usage"}) == "; did you mean #installation?"
    assert suggest("zzz", {"installation"}) == ""


def test_suggestion_in_result(tmp_path):
    (tmp_path / "a.md").write_text("# Getting Started\n[x](#getting-startd)\n")
    (r,) = run([tmp_path], Config())
    assert "did you mean #getting-started?" in r.reason
