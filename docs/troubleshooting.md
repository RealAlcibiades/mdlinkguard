# Troubleshooting

- **A site returns 403 or 429 but works in a browser.** Many sites block automated clients. Lower `--rate-limit`, or add the URL to `ignore`.
- **An anchor is reported missing but the heading exists.** mdlinkguard follows GitHub's slug rules. Other renderers may differ; use an explicit `<a id="...">` to be safe.
- **Links in generated files are noisy.** Exclude them with `-x 'build/*'`.
- **Watch mode does not notice changes.** It polls every second for added, removed, or modified `.md`, `.markdown`, and `.mdx` files under the given paths.
