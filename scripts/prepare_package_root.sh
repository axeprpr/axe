#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <output-dir>" >&2
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_dir="$1"

mkdir -p "${out_dir}/usr/lib/axe"
mkdir -p "${out_dir}/usr/bin"

cp -R "${repo_root}/axe_cli" "${out_dir}/usr/lib/axe/"
cp "${repo_root}/packaging/axe-entrypoint" "${out_dir}/usr/bin/axe"

chmod 0755 "${out_dir}/usr/bin/axe"
