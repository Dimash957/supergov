# eGov API Integration - Setup для Windows (PowerShell)
# Запустить: .\egov-setup.ps1

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "🚀 eGov API Integration - Setup (Windows)" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan

# 1. Проверить что находимся в правильной папке
if (-not (Test-Path "app/main.py")) {
    Write-Host "❌ Пожалуйста, запустите из папки backend/" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Вы в папке backend/`n" -ForegroundColor Green

# 2. Проверить интеграцию
Write-Host "🔍 Проверка интеграции..." -ForegroundColor Yellow
python check_egov_integration.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Проверка не пройдена" -ForegroundColor Red
    exit 1
}

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host "✅ Интеграция успешна!" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan

Write-Host "`n🎯 Команды для запуска:`n" -ForegroundColor Green

Write-Host "  1. Настроить конфигурацию:" -ForegroundColor Yellow
Write-Host "     copy .env.egov.example .env" -ForegroundColor White
Write-Host "     # Отредактируйте .env с вашими значениями`n" -ForegroundColor Gray

Write-Host "  2. Запустить сервер:" -ForegroundColor Yellow
Write-Host "     python -m uvicorn app.main:app --reload --port 8000`n" -ForegroundColor White

Write-Host "  3. В другом терминале протестировать:" -ForegroundColor Yellow
Write-Host "     python test_egov_all_functions.py`n" -ForegroundColor White

Write-Host "====================================================================" -ForegroundColor Cyan
