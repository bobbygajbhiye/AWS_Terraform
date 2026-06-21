#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build/lambda_package"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

python -m pip install --upgrade pip
python -m pip install --target "$BUILD_DIR" -r "$ROOT_DIR/lambda_src/requirements-lambda.txt"
cp "$ROOT_DIR"/lambda_src/*.py "$BUILD_DIR"/

find "$BUILD_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +

