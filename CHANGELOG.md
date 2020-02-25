# Changelog

## 0.1.1

- Replaced vendored `pexpect` and `ptyprocess` copies with external package dependencies.
- Added an offline self-contained bundle artifact to the release pipeline.
- Tightened release automation and package dependency handling.

## 0.1.0

- Ported the tool to Python 3 and stabilized terminal handling.
- Added regression tests and cleaned Python build artifacts from the repository.
- Improved SSH/SCP behavior for batch command execution and file copy workflows.
- Added configurable host prefix, connection timeout, identity file support, dry-run mode, and batch concurrency.
- Packaged the project as an installable Python CLI with `pyproject.toml`.
- Added GitHub Actions for CI, release builds, and Linux package generation.
- Reworked the README with installation, usage, scenarios, and FAQ sections.

## Before 0.1.0

- Early repository history contains the original shell-oriented utility implementation and incremental fixes.
