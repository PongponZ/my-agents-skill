#!/usr/bin/env sh
# macOS / Linux wrapper:  ./install.sh            (interactive menu)
#                         ./install.sh all        (Claude Code + Codex + Blender modules + zip packages)
DIR="$(cd "$(dirname "$0")" && pwd)"
PY="$(command -v python3 || command -v python)"
[ -z "$PY" ] && { echo "Python 3.10+ is required"; exit 1; }
exec "$PY" "$DIR/install_skills.py" "$@"
