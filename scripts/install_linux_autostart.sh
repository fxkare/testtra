#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_PATH="$ROOT_DIR/dist/HizliCeviri"
AUTOSTART_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/hizli-ceviri.desktop"

if [[ ! -x "$APP_PATH" ]]; then
  echo "Executable not found: $APP_PATH"
  echo "Run scripts/build_linux.sh first."
  exit 1
fi

mkdir -p "$AUTOSTART_DIR"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Hizli Ceviri
Comment=Fast Turkish translator
Exec=$APP_PATH
Path=$ROOT_DIR/dist
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

chmod +x "$DESKTOP_FILE"
echo "Autostart entry installed: $DESKTOP_FILE"
