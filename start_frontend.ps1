# Script para iniciar el frontend
Write-Host "Iniciando servidor HTTP del frontend..." -ForegroundColor Green
Write-Host "Frontend disponible en: http://127.0.0.1:8080" -ForegroundColor Cyan
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host ""

cd .\frontend
python -m http.server 8080 --bind 127.0.0.1
