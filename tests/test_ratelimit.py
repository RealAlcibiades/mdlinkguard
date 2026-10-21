from mdlinkguard.config import load_config
from mdlinkguard.ratelimit import HostRateLimiter


class FakeClock:
    def __init__(self):
        self.t, self.slept = 0.0, []
    def __call__(self):
        return self.t
    def sleep(self, d):
        self.slept.append(round(d, 3))
        self.t += d


def test_spacing_per_host():
    c = FakeClock()
    rl = HostRateLimiter(per_host={"github.com": 2}, clock=c, sleep=c.sleep)
    for _ in range(3):
        rl.wait("https://api.github.com/x")
    rl.wait("https://example.com/")  # unlimited host
    assert c.slept == [0.5, 0.5]


def test_default_rate_and_config(tmp_path):
    assert HostRateLimiter(4).rate_for("a.b") == 4
    (tmp_path / ".mdlinkguard.toml").write_text('rate_limit = 1\n[host_rate_limits]\n"github.com" = 2\n')
    cfg = load_config(None, tmp_path)
    assert cfg.rate_limit == 1 and cfg.host_rate_limits == {"github.com": 2}
