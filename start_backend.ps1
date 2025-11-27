# Script para iniciar el backend
Write-Host "Iniciando backend (FastAPI + Uvicorn)..." -ForegroundColor Green
Write-Host "Backend disponible en: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "Documentación API: http://127.0.0.1:5000/docs" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 5000
