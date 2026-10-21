# Changelog

All notable changes to this project will be documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.5.0] - 2026-10-21

### Added
- Per-host rate limiting: `--rate-limit RPS` caps requests per second to any single host, and `[host_rate_limits]` in config sets overrides per domain (subdomains inherit from their parent, so `api.github.com` uses the `github.com` limit).
- `--watch` / `-w`: re-runs the check whenever a Markdown file is added, removed, or modified. Uses stdlib polling, so it adds no dependencies.

## [0.4.0] - 2026-10-21

### Added
- HTML `<a href>` and `<img src>` tags inside Markdown are now checked (code blocks and inline code are still skipped).
- `.mdx` files: top-level `import`/`export` statements are ignored instead of being scanned for links.
- Redirect reporting: `--redirects` lists external links that redirect and where they end up; `--fail-on-redirect` treats them as broken. JSON output includes a `redirect` field.

### Changed
- `http_status` now returns `(status, final_url)`. Custom fetchers may return either an int or that tuple.

## [0.3.0] - 2026-10-21

### Added
- `--format github`: emits GitHub Actions workflow commands so broken links show up as inline annotations on pull requests.
- `--format sarif`: SARIF 2.1.0 output for GitHub code scanning and other SARIF viewers.
- `--stats`: prints a summary to stderr (links by kind, top failure reasons, files with the most broken links).

## [0.2.0] - 2026-10-21

### Added
- On-disk cache for external URL results with a configurable TTL (`--cache`, `--cache-ttl`, `cache`/`cache_ttl` in config). Only successful checks are cached, so failures are always re-verified.
- Broken `#anchor` reports now suggest the closest existing heading (e.g. `missing anchor #instalation; did you mean #installation?`).

## [0.1.0] - 2026-10-21

### Added
- Initial release: inline, image, reference, and autolink extraction
- Relative file and `#anchor` checks with GitHub-style slugs
- Optional concurrent HTTP(S) checks with timeouts and retries
- Ignore and exclude patterns via CLI or TOML config
- Text and JSON output, plus CI-friendly exit codes
