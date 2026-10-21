import json

from mdlinkguard.checker import Result
from mdlinkguard.cli import main
from mdlinkguard.reporters import github, sarif

R = [Result("docs/a.md", 3, "x.md", "inline", False, "file not found"), Result("b.md", 1, "#a", "inline", True)]


def test_github_annotations():
    assert github(R) == "::error file=docs/a.md,line=3,title=Broken link::x.md (file not found)"


def test_sarif_shape():
    doc = json.loads(sarif(R))
    (res,) = doc["runs"][0]["results"]
    assert doc["version"] == "2.1.0"
    assert res["locations"][0]["physicalLocation"]["region"]["startLine"] == 3


def test_cli_github_format(tmp_path, capsys, monkeypatch):
    (tmp_path / "a.md").write_text("[x](missing.md)\n")
    monkeypatch.chdir(tmp_path)
    assert main(["--format", "github"]) == 1
    assert capsys.readouterr().out.startswith("::error file=a.md,line=1")


def test_stats():
    from mdlinkguard.reporters import stats
    s = stats(R)
    assert "2 links in 2 files, 1 broken" in s and "file not found" in s and "inline=2" in s
