#!/usr/bin/env bash
#
# scan-secrets.sh — the local mirror of the CI secret-scan job.
#
# REPO-BASELINE.md §4 asks for a script that reproduces a CI job 1:1, so that
# "it passed locally" means something. The default mode scans full history
# exactly as .github/workflows/secret-scan.yml does.
#
# Usage:
#   scripts/scan-secrets.sh            # full history (what CI runs)
#   scripts/scan-secrets.sh --staged   # staged changes only (what the hook runs)
#   scripts/scan-secrets.sh --dir      # working tree as files, ignoring history

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
CONFIG="${REPO_ROOT}/.gitleaks.toml"
MODE="${1:-history}"

red()   { printf '\033[0;31m%s\033[0m\n' "$*"; }
green() { printf '\033[0;32m%s\033[0m\n' "$*"; }
dim()   { printf '\033[0;90m%s\033[0m\n' "$*"; }

if [ ! -f "${CONFIG}" ]; then
  red "scan-secrets: .gitleaks.toml missing from the repository root."
  exit 1
fi

# Resolve the mode BEFORE choosing a runner, so an unknown mode prints usage
# rather than silently scanning something else — which would also make the
# pre-commit hook's "reproduce with --staged" hint reproduce the wrong scan.
case "${MODE}" in
  --staged|--dir) ;;
  history|"") MODE=history ;;
  *)
    red "Unknown mode: ${MODE}"
    echo "Usage: scripts/scan-secrets.sh [--staged|--dir]"
    exit 2
    ;;
esac

# v8.19 renamed detect/protect to git/dir and moved the target from --source to a
# positional argument. Probe rather than assume, so a scanner upgrade does not
# turn this red for the wrong reason.
args_native() {
  case "${MODE}" in
    history) if gitleaks git --help >/dev/null 2>&1;
             then echo "git ${REPO_ROOT}"; else echo "detect --source=${REPO_ROOT}"; fi ;;
    --staged) if gitleaks git --help >/dev/null 2>&1;
             then echo "git --staged ${REPO_ROOT}"; else echo "protect --staged --source=${REPO_ROOT}"; fi ;;
    --dir)   if gitleaks dir --help >/dev/null 2>&1;
             then echo "dir ${REPO_ROOT}"; else echo "detect --no-git --source=${REPO_ROOT}"; fi ;;
  esac
}

if command -v gitleaks >/dev/null 2>&1; then
  dim "scan-secrets: using the gitleaks binary (${MODE})"
  # shellcheck disable=SC2046  # word splitting is the point: these are argv words
  set +e
  gitleaks $(args_native) --config="${CONFIG}" --redact --no-banner --verbose --exit-code 2
  STATUS=$?
  set -e
elif command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  dim "scan-secrets: gitleaks not on PATH; using the container image (${MODE})"
  IMAGE="ghcr.io/gitleaks/gitleaks:latest"
  case "${MODE}" in
    history)  SUB=(git /repo) ;;
    --staged) SUB=(git --staged /repo) ;;
    --dir)    SUB=(dir /repo) ;;
  esac
  set +e
  docker run --rm -v "${REPO_ROOT}:/repo" -w /repo "${IMAGE}" "${SUB[@]}" \
    --config=/repo/.gitleaks.toml --redact --no-banner --verbose --exit-code 2
  STATUS=$?
  set -e
else
  red "scan-secrets: no scanner available (need gitleaks or Docker)."
  exit 1
fi

if [ "${STATUS}" -eq 0 ]; then
  green "scan-secrets: clean."
  exit 0
fi
if [ "${STATUS}" -eq 2 ]; then
  red "scan-secrets: findings above. ROTATE the credential first, then clean history."
  exit 2
fi
red "scan-secrets: the scanner failed to run (exit ${STATUS}). That is a tooling"
red "failure, not a clean result."
exit 1
