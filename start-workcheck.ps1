param(
    [ValidateRange(1024, 65535)]
    [int]$Port = 8501
)

# Use this file's folder, even when PowerShell was opened somewhere else.
Set-Location -LiteralPath $PSScriptRoot
$workcheckPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $workcheckPython)) {
    Write-Error 'WorkCheck is not set up yet. Follow the one-time setup commands in README.md.'
    exit 1
}
Write-Host "Open http://127.0.0.1:$Port . Keep this terminal open; stop with Ctrl+C."
& $workcheckPython -m streamlit run (Join-Path $PSScriptRoot 'app.py') --server.address 127.0.0.1 --server.port $Port --browser.gatherUsageStats false
exit $LASTEXITCODE
