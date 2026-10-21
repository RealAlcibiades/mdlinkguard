from mdlinkguard.cache import UrlCache
from mdlinkguard.checker import run
from mdlinkguard.config import Config


def test_cache_skips_second_fetch(tmp_path):
    (tmp_path / "a.md").write_text("[w](https://example.com)\n")
    cache = tmp_path / "c.json"
    calls = []
    def fetch(u, t):
        calls.append(u)
        return 200
    cfg = Config(check_external=True, cache=str(cache))
    run([tmp_path / "a.md"], cfg, fetch)
    run([tmp_path / "a.md"], cfg, fetch)
    assert calls == ["https://example.com"]


def test_failures_not_cached_and_ttl(tmp_path):
    c = UrlCache(tmp_path / "c.json", ttl=0)
    c.put("u", "HTTP 404")
    assert c.get("u") is None
    c.put("v", "")
    c.data["v"]["ts"] -= 10
    assert c.get("v") is None
