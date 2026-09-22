#!/bin/zsh
cd "$(dirname "$0")" || exit 1
python3 tools/play_cargo_review.py
