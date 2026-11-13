#!/usr/bin/env bash
# Reproduces revision 1 end to end (macOS, Linux, Git Bash on Windows).
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python}"
"$PY" scripts/revision_model.py data results
"$PY" scripts/make_figures.py results figures
"$PY" scripts/make_supplement.py . supplementary
"$PY" scripts/check_run.py .
