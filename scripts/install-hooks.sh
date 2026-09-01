#!/usr/bin/env bash
#
# install-hooks.sh — point this clone's git hooks at scripts/hooks/.
#
# Uses core.hooksPath rather than copying files into .git/hooks/, so a hook
# improved later takes effect on `git pull` instead of on everyone remembering
# to re-run this. A copied hook is a fork of the hook.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
git -C "${REPO_ROOT}" config core.hooksPath scripts/hooks
chmod +x "${REPO_ROOT}"/scripts/hooks/* 2>/dev/null || true

printf '\033[0;32m%s\033[0m\n' "hooks installed: core.hooksPath = scripts/hooks"
echo
echo "The pre-commit hook scans staged changes for secrets and needs either the"
echo "gitleaks binary or Docker. It fails rather than warns when neither is"
echo "present — a hook whose protection depends on your toolchain is not a hook."
echo
echo "Undo with: git config --unset core.hooksPath"
