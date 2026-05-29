#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements-linux.txt

python -m PyInstaller \
  --noconfirm \
  --clean \
  --noconsole \
  --onefile \
  --name HizliCeviri \
  --collect-all customtkinter \
  --collect-all pynput \
  --collect-all pystray \
  translator_app.py

echo "Build complete: $ROOT_DIR/dist/HizliCeviri"
