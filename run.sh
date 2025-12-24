#!/bin/bash
# Launch Tempus Application
# Double-click to run or execute: ./run.sh

cd "$(dirname "$0")"
uv run tempus-desktop "$@"
