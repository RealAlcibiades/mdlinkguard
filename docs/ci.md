# CI recipes

## GitHub Action with annotations

```yaml
name: links
on: [pull_request]
jobs:
  links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: RealAlcibiades/mdlinkguard@v0.5.0
```

## Upload SARIF to code scanning

```yaml
      - run: pip install git+https://github.com/RealAlcibiades/mdlinkguard
      - run: mdlinkguard --format sarif > links.sarif || true
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: links.sarif
```

## Nightly external check with cache

```yaml
on:
  schedule: [{ cron: "0 6 * * *" }]
steps:
  - uses: actions/checkout@v4
  - uses: actions/cache@v4
    with:
      path: .mdlinkguard-cache.json
      key: mdlinkguard-${{ github.run_id }}
      restore-keys: mdlinkguard-
  - uses: RealAlcibiades/mdlinkguard@v0.5.0
    with:
      external: "true"
      args: "--cache --rate-limit 2"
```
