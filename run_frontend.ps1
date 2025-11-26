# run_frontend.ps1
# Starts a simple static server for the `frontend/` folder and opens the default browser.
# Usage: Right-click -> Run with PowerShell, or from PowerShell: .\run_frontend.ps1

$ErrorActionPreference = 'Stop'

$frontendDir = Join-Path $PSScriptRoot 'frontend'
if (-not (Test-Path $frontendDir)) {
    Write-Error "No se encontró la carpeta 'frontend' en: $PSScriptRoot"
    exit 1
}

Push-Location $frontendDir
Write-Host "Iniciando servidor estático en http://127.0.0.1:8080 (carpeta: $frontendDir)" -ForegroundColor Green

# Start the server in a separate process
$proc = Start-Process -FilePath "python" -ArgumentList "-m","http.server","8080","--bind","127.0.0.1" -WindowStyle Minimized -PassThru
Start-Sleep -Milliseconds 800

# Open default browser to the frontend URL
Start-Process "http://127.0.0.1:8080"

Write-Host "Servidor iniciado (PID $($proc.Id)). Para detenerlo, cierre esta ventana o ejecute: Stop-Process -Id $($proc.Id)" -ForegroundColor Yellow
Write-Host "Presiona ENTER en esta consola para detener el servidor y salir..." -ForegroundColor Cyan
Read-Host | Out-Null

try {
    Write-Host "Deteniendo servidor (PID $($proc.Id))..." -ForegroundColor Yellow
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
} catch {
    # ignore
}

Pop-Location
Write-Host "Listo." -ForegroundColor Green
