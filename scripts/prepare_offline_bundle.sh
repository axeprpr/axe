#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <output-dir>" >&2
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_dir="$1"
venv_dir="$(mktemp -d)"

cleanup() {
  rm -rf "${venv_dir}"
}
trap cleanup EXIT

mkdir -p "${out_dir}/bin"
mkdir -p "${out_dir}/lib"

python3 -m venv "${venv_dir}"
"${venv_dir}/bin/pip" install --upgrade pip
"${venv_dir}/bin/pip" install --no-compile --target "${out_dir}/lib" "${repo_root}"
cp "${repo_root}/packaging/axe-bundle-entrypoint" "${out_dir}/bin/axe"

chmod 0755 "${out_dir}/bin/axe"
