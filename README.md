# mdlinkguard

[![License: MIT](https://img.shields.io/github/license/RealAlcibiades/mdlinkguard)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](pyproject.toml)
[![Release](https://img.shields.io/github/v/release/RealAlcibiades/mdlinkguard)](https://github.com/RealAlcibiades/mdlinkguard/releases)

Find broken links in your Markdown before your readers do.

`mdlinkguard` scans Markdown files and folders and reports:

- **Missing files**: relative links such as `[guide](docs/guide.md)` or images that point nowhere
- **Bad anchors**: `#heading` fragments that don't match any heading, using GitHub-style slugs, duplicate-heading suffixes, and `<a id>` tags
- **Dead URLs** (optional): concurrent HTTP(S) checks with timeouts, retries, per-host rate limits, and an on-disk cache
- **Redirects** (optional): external links that moved, so you can update them
- **Typos**: broken anchors come with a "did you mean" suggestion

It understands inline links, images, reference-style links, autolinks, and HTML `<a href>` / `<img src>` tags, and it skips anything inside code blocks or inline code. The only dependency is the standard library (plus `tomli` on Python < 3.11).

## Install

```bash
pip install git+https://github.com/RealAlcibiades/mdlinkguard
```

## Usage

```bash
mdlinkguard                      # scan the current directory
mdlinkguard README.md docs/      # specific files or folders
mdlinkguard --external           # also check http(s) links
mdlinkguard --format json        # machine-readable output
mdlinkguard --format github      # inline annotations on pull requests
mdlinkguard --format sarif > links.sarif   # GitHub code scanning
mdlinkguard -e --cache --rate-limit 2      # fast, polite repeat runs
mdlinkguard --watch docs/        # re-check as you edit
mdlinkguard --stats              # summary by kind, reason, and file
mdlinkguard -i '^https://localhost' -x 'node_modules/*'
```

Exit codes: `0` means all links are OK, `1` means at least one is broken, and `2` means a usage error.

Example output:

```
README.md:3: BROKEN nope.md (file not found)
README.md:5: BROKEN docs/guide.md#missing (missing anchor #missing)
6 links checked, 2 broken.
```

### Options

| Flag | Description |
|------|-------------|
| `-e, --external` | Check HTTP(S) URLs |
| `-i, --ignore REGEX` | Ignore link targets matching a regex (repeatable) |
| `-x, --exclude GLOB` | Skip files matching a glob (repeatable) |
| `-c, --config FILE` | Use a specific TOML config |
| `--timeout SECS` | HTTP timeout (default 10) |
| `--retries N` | Retries on timeouts, 429 and 5xx (default 2) |
| `-j, --concurrency N` | Parallel HTTP requests (default 8) |
| `--rate-limit RPS` | Max requests per second to any one host |
| `--cache [FILE]` | Cache successful external results (default `.mdlinkguard-cache.json`) |
| `--cache-ttl SECS` | Cache lifetime (default 86400) |
| `--redirects` | Report external links that redirect |
| `--fail-on-redirect` | Treat redirects as broken |
| `--format text\|json\|github\|sarif` | Output format |
| `--stats` | Print a summary report to stderr |
| `-w, --watch` | Re-check when Markdown files change |
| `-v, --verbose` | Also list working links |

## Configuration

Put settings in `.mdlinkguard.toml` or under `[tool.mdlinkguard]` in `pyproject.toml`. CLI flags extend or override the config.

```toml
[tool.mdlinkguard]
ignore = ["^https://example\\.com", "^http://localhost"]
exclude = ["CHANGELOG.md", "vendor/*"]
check_external = false
timeout = 10
retries = 2
concurrency = 8
rate_limit = 0          # requests/second per host, 0 = unlimited
cache = ".mdlinkguard-cache.json"
cache_ttl = 86400
fail_on_redirect = false

[tool.mdlinkguard.host_rate_limits]
"github.com" = 2
```

See [docs/configuration.md](docs/configuration.md) for every option.

## CI

### GitHub Action

```yaml
- uses: actions/checkout@v4
- uses: RealAlcibiades/mdlinkguard@v0.5.0
  with:
    paths: "README.md docs"
    external: "false"
```

Broken links show up as annotations on the pull request diff. More recipes are in [docs/ci.md](docs/ci.md).

### Plain pip

```yaml
- uses: actions/setup-python@v5
  with: { python-version: "3.12" }
- run: pip install git+https://github.com/RealAlcibiades/mdlinkguard
- run: mdlinkguard .
```

### pre-commit

```yaml
repos:
  - repo: https://github.com/RealAlcibiades/mdlinkguard
    rev: v0.1.0
    hooks:
      - id: mdlinkguard
```

## FAQ

**How is this different from other link checkers?** It is a small, dependency-free Python tool focused on Markdown: it understands GitHub heading slugs and suggests fixes for anchor typos, and it emits GitHub annotations and SARIF directly. Larger tools such as lychee or markdown-link-check cover more formats; pick whatever fits your stack.

**Will it hammer external sites?** External checks are off by default. When enabled, each URL is checked once per run, and you can add `--rate-limit` and `--cache` to stay polite.

**Why is a working link reported as broken?** Some sites block automated HEAD/GET requests. Add the URL to `ignore`. See [docs/troubleshooting.md](docs/troubleshooting.md).

## License

MIT. See [LICENSE](LICENSE). Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
