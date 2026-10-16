#!/bin/bash
cd "$(dirname "$0")"
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi
$PYTHON_CMD -m pip install -r requirements.txt --quiet --disable-pip-version-check
$PYTHON_CMD start_app.py
