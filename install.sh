#!/usr/bin/env bash

set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
axe_path="${repo_dir}/axe"
alias_line="alias axe='${axe_path}'"

update_rc_file() {
  local rc_file="$1"
  touch "${rc_file}"
  sed -i '/alias axe=/d' "${rc_file}"
  printf '%s\n' "${alias_line}" >> "${rc_file}"
}

update_rc_file "${HOME}/.bashrc"
update_rc_file "${HOME}/.zshrc"

printf 'Installed alias: %s\n' "${alias_line}"
