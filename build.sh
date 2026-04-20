#!/usr/bin/env bash
# Local build script (Linux). For Windows use build.ps1.
set -e

echo "=== ImageProcessor — local build ==="

pip install -r requirements.txt pyinstaller --quiet
rm -rf build dist

pyinstaller imageprocessor.spec --noconfirm

tar -czf ImageProcessor-linux-x86_64.tar.gz -C dist ImageProcessor

echo ""
echo "Done → ImageProcessor-linux-x86_64.tar.gz"
echo "Run: dist/ImageProcessor/ImageProcessor"
