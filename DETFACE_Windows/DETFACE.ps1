# DETFACE - PowerShell Launcher
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "    DETFACE - Sistema de Reconhecimento Facial" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Python não encontrado" }
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "SOLUÇÃO:" -ForegroundColor Yellow
    Write-Host "1. Baixe Python de: https://python.org" -ForegroundColor White
    Write-Host "2. Marque 'Add Python to PATH' na instalação" -ForegroundColor White
    Write-Host "3. Reinicie o computador" -ForegroundColor White
    Write-Host ""
    Start-Process "https://python.org/downloads/"
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar dependências
Write-Host "Verificando dependências..." -ForegroundColor Yellow
try {
    python -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL" 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Dependências em falta" }
    Write-Host "✓ Dependências OK" -ForegroundColor Green
} catch {
    Write-Host "⚠ Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    # Verificar novamente
    python -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Erro na instalação!" -ForegroundColor Red
        Write-Host "Execute: instalar_dependencias.bat" -ForegroundColor Yellow
        Read-Host "Pressione Enter para sair"
        exit 1
    }
}

# Executar aplicação
Write-Host ""
Write-Host "🚀 Iniciando DETFACE..." -ForegroundColor Green
Write-Host "A interface gráfica abrirá em instantes..." -ForegroundColor White
Write-Host ""

python detface_desktop.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Erro ao executar aplicação!" -ForegroundColor Red
    Write-Host "Verifique os logs na pasta 'logs'" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
}
