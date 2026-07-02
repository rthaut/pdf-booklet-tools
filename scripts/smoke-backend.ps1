$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"

$env:PYTHONPATH = if ($env:PYTHONPATH) {
    "$backendDir$([IO.Path]::PathSeparator)$env:PYTHONPATH"
} else {
    $backendDir
}

python (Join-Path $backendDir "scripts\smoke_process_pdf.py")
