#!/usr/bin/env sh
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-research.txt
echo 'Installed. ./run.sh'
