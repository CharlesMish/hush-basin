#!/bin/zsh
set -euo pipefail
SESSION_ROOT="${0:A:h}"
exec /usr/bin/env python3 "$SESSION_ROOT/project/tools/launch_a1_capture.py" --session-root "$SESSION_ROOT" "$@"
