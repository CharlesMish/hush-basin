#!/bin/zsh
set -e
cd -- "${0:A:h}"
exec python3 tools/play_story.py
