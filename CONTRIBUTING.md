# Contributing

Thanks for helping out!

1. Fork the repo and create a branch.
2. `python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'`
3. Make your change and add tests in `tests/`. Tests must run offline, so use the `fetch` hook to fake HTTP.
4. Run `pytest` and `mdlinkguard .` (the repo checks its own docs).
5. Add a line under "Unreleased" in `CHANGELOG.md` and open a pull request.

When you report a bug, please include a minimal Markdown snippet that reproduces it.
