# Agent instructions

For AI coding assistants (Claude Code, GitHub Copilot, Codex, Cursor and others) working in this repository.
People should start with [CONTRIBUTING.md](CONTRIBUTING.md).

## What this is

A Home Assistant custom integration (`custom_components/degel`, distributed through HACS) for Québec's spring
thaw periods, from Transports Québec's WFS service. Its *Thaw season* binary sensor drives card visibility;
the companion card is [Dégel-Carte](https://github.com/olivierouellet/Degel-Carte).

## Before you finish

```bash
uv venv --python 3.13 && uv pip install -r requirements_test.txt   # once
ruff check && ruff format --check
pytest
```

All must pass; CI runs the same, plus HACS and hassfest validation.

## Conventions

* **French first.** Every document is bilingual, French section first; a change users see goes in both.
* `strings.json` is English and is copied unchanged to `translations/en.json`; `translations/fr.json` has
  the same keys. A test enforces both.
* **Tests never call the real service.** They use responses recorded in `tests/fixtures/` (see
  CONTRIBUTING.md for the `curl` line). Don't add tests that reach the network.
* The date rules in `season.py` are mirrored in Dégel-Carte's `src/season.ts`: change one, change the other.
* The dates are Transports Québec's: never guess, shift or correct them.
* The manifest has no `requirements`; keep it that way. Python 3.13, Home Assistant 2025.1 or later.
* A release bumps `version` in `manifest.json` in a commit titled `[Integration] Version X.Y.Z`, then a
  GitHub release tagged `vX.Y.Z`.
* The icon's source is `assets/icon.svg`; `brand/icon.png` (256 px) and `brand/icon@2x.png` (512 px) are
  exported from it.

## Commits and publishing

* Commit titles read `[Topic] What changed`, one topic per commit. Topics in use: `[Integration]`, `[Tests]`, `[Tooling]`, `[Docs]`.
* **Never commit, push, tag, publish a release, or open an issue or pull request unless asked.** Approval for
  one of these is not approval for the next.
* `main` is protected against force-pushes and deletion: never rewrite history that is already pushed.
* Never post comments on issues or pull requests on the user's behalf without their review.

## AI policy

This project follows its [AI policy](AI_POLICY.md): a person reviews and understands every change, no
autonomous contributions, and nothing is posted on someone's behalf without their review.
