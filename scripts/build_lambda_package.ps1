$ErrorActionPreference = "Stop"

$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
$BuildDir = Join-Path $RootDir "build\lambda_package"

if (Test-Path $BuildDir) {
    Remove-Item -LiteralPath $BuildDir -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

python -m pip install --upgrade pip
python -m pip install --target $BuildDir -r (Join-Path $RootDir "lambda_src\requirements-lambda.txt")
Copy-Item -Path (Join-Path $RootDir "lambda_src\*.py") -Destination $BuildDir

