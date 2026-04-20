# Local build script for Windows.
# Run from repo root: .\build.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "=== ImageProcessor — local build ===" -ForegroundColor Cyan

pip install -r requirements.txt pyinstaller --quiet

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

pyinstaller imageprocessor.spec --noconfirm

Compress-Archive -Path dist\ImageProcessor -DestinationPath ImageProcessor-windows-x86_64.zip -Force

Write-Host ""
Write-Host "Done -> ImageProcessor-windows-x86_64.zip" -ForegroundColor Green
Write-Host "Run:    dist\ImageProcessor\ImageProcessor.exe"
