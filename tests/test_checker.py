import json
from pathlib import Path

from mdlinkguard.checker import check_url, run
from mdlinkguard.cli import main
from mdlinkguard.config import Config, load_config


def make(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("# Setup Steps\n")
    (tmp_path / "README.md").write_text(
        "# Intro\n[ok](docs/guide.md#setup-steps)\n[bad](nope.md)\n"
        "[anchor](#intro)\n[badanchor](docs/guide.md#missing)\n[web](https://example.com)\n"
    )


def test_local_links(tmp_path):
    make(tmp_path)
    res = run([tmp_path], Config())
    broken = {r.target for r in res if not r.ok}
    assert broken == {"nope.md", "docs/guide.md#missing"}


def test_external_with_fake_fetch(tmp_path):
    make(tmp_path)
    cfg = Config(check_external=True, retries=0)
    res = run([tmp_path], cfg, fetch=lambda u, t: 404)
    assert any(r.target == "https://example.com" and r.reason == "HTTP 404" for r in res)


def test_retry_then_success():
    calls = []
    def fetch(u, t):
        calls.append(1)
        if len(calls) < 2:
            raise TimeoutError("slow")
        return 200
    assert check_url("https://x.test", Config(retries=2), fetch) == ""
    assert len(calls) == 2


def test_ignore_and_exclude(tmp_path):
    make(tmp_path)
    res = run([tmp_path], Config(ignore=[r"nope\.md"], exclude=["*guide.md"]))
    assert "nope.md" not in {r.target for r in res if not r.ok}


def test_config_file(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[tool.mdlinkguard]\nignore = ["^x"]\ntimeout = 3\n')
    cfg = load_config(None, tmp_path)
    assert cfg.ignore == ["^x"] and cfg.timeout == 3


def test_cli_json_exit_code(tmp_path, capsys, monkeypatch):
    make(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert main(["--format", "json", "."]) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["broken"] == 2


def test_cli_clean(tmp_path, monkeypatch):
    (tmp_path / "a.md").write_text("# A\n[self](#a)\n")
    monkeypatch.chdir(tmp_path)
    assert main([]) == 0
