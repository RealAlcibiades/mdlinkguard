# Configuration

mdlinkguard reads `.mdlinkguard.toml` in the current directory, or `[tool.mdlinkguard]` in `pyproject.toml`. Pass `-c FILE` to use another file. CLI flags extend list options (`ignore`, `exclude`) and override scalar ones.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `ignore` | list of regex | `[]` | Link targets to skip |
| `exclude` | list of glob | `[]` | Files to skip |
| `check_external` | bool | `false` | Check http(s) URLs |
| `timeout` | float | `10` | HTTP timeout in seconds |
| `retries` | int | `2` | Retries for timeouts, 429, and 5xx |
| `concurrency` | int | `8` | Parallel HTTP requests |
| `rate_limit` | float | `0` | Requests per second per host (0 = unlimited) |
| `host_rate_limits` | table | `{}` | Per-domain overrides; subdomains inherit |
| `cache` | string | unset | Path of the result cache file |
| `cache_ttl` | float | `86400` | Cache lifetime in seconds |
| `fail_on_redirect` | bool | `false` | Treat redirecting links as broken |

Only successful external checks are cached, so a failing link is always re-checked.
