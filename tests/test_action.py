from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_action_metadata():
    text = (ROOT / "action.yml").read_text()
    assert "using: composite" in text
    assert "--format github" in text
    for name in ("paths:", "external:", "args:"):
        assert name in text
