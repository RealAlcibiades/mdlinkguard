# mdlinkguard

Find broken links in your Markdown before your readers do.

`mdlinkguard` scans Markdown files and folders and reports:

- **Missing files**: relative links such as `[guide](docs/guide.md)` or images that point nowhere
- **Bad anchors**: `#heading` fragments that don't match any heading, using GitHub-style slugs, duplicate-heading suffixes, and `<a id>` tags
- **Dead URLs** (optional): concurrent HTTP(S) checks with timeouts and retries

It understands inline links, images, reference-style links, and autolinks, and it skips anything inside code blocks or inline code. The only dependency is the standard library (plus `tomli` on Python < 3.11).

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
| `--format text\|json` | Output format |
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
```

## CI

### GitHub Actions

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

## License

MIT. See [LICENSE](LICENSE). Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
