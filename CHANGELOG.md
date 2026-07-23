# Changelog

All notable changes to this skill are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-07-23

### Added
- `scripts/install.sh` — One-line installer (clone + symlink + verify)
- `scripts/validate.sh` — Self-validation script (22 checks)
- `examples/prototype-todo-app/` — Real, runnable Todo app demonstrating
  the `new-feature` example end-to-end (server + client + e2e test)
- `INSTALL.md` — Standalone installation guide with 5 install methods
- `examples/` and `references/` now have frontmatter (consistent format)
- `version`, `license`, `metadata` fields added to all `agents/*.md`
- `allowed-tools` field added to `SKILL.md`
- `CONTRIBUTING.md` — How to add new workers, examples, or improve leader template
- `CHANGELOG.md` — This file
- GitHub Actions CI for skill validation on every PR

### Changed
- `SKILL.md` description: changed from multi-line YAML `|` to single-line quoted
  string for better tool compatibility
- `README.md` improved: clearer quickstart, more accurate comparison table
- All 4 examples now have frontmatter with `type: example` marker

### Fixed
- `examples/prototype-todo-app/test_e2e.py` had unused `port` variable
  and wrong URL paths — fixed in v1.1.0

## [1.0.0] - 2026-07-22

### Added
- Initial release
- `SKILL.md` with full Team Mode workflow (7 steps)
- 6 sub-agent role templates (leader + 5 workers + verifier)
- 4 worked examples (refactor, bug-hunt, new-feature, research-then-implement)
- 3 reference documents (verification-checklist, deepseek-setup, troubleshooting)
- `README.md` with comparison table (Zcode skill vs Mavis native)
- `LICENSE` (MIT)
- `.gitignore`

[1.1.0]: https://github.com/YOUR_USERNAME/mavis-team-mode-skill/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/YOUR_USERNAME/mavis-team-mode-skill/releases/tag/v1.0.0
