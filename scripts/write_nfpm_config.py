#!/usr/bin/env python3

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 5:
        print("Usage: write_nfpm_config.py <output> <version> <arch> <package-format>", file=sys.stderr)
        return 1

    output, version, arch, package_format = sys.argv[1:]
    config = f"""name: axe-cli
arch: {arch}
platform: linux
version: {version}
section: utils
priority: optional
maintainer: axe contributors
description: Batch SSH and SCP helper built on pexpect
homepage: https://github.com/axeprpr/axe
contents:
  - src: ./dist/package-root/usr/lib/axe/
    dst: /usr/lib/axe
  - src: ./dist/package-root/usr/bin/axe
    dst: /usr/bin/axe
    file_info:
      mode: 0755
depends:
  - python3
"""
    if package_format == "rpm":
        config += "rpm:\n  compression: gzip\n"

    Path(output).write_text(config, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
