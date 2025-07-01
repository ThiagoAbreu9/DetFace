@echo off
title DETFACE - Sistema de Reconhecimento Facial
color 0A
echo.
echo ===============================================
echo      DETFACE - Sistema de Reconhecimento Facial
echo              Iniciando Aplicacao...
echo ===============================================
echo.

REM Verificar se Python esta instalado
echo [INFO] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo SOLUCAO:
    echo 1. Baixe Python 3.8+ de: https://python.org
    echo 2. Durante a instalacao, marque "Add Python to PATH"
    echo 3. Reinicie o computador apos a instalacao
    echo 4. Execute este arquivo novamente
    echo.
    pause
    exit /b 1
)

python --version
echo [OK] Python encontrado!
echo.

REM Verificar e instalar dependencias
echo [INFO] Verificando dependencias...
python -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL" 2>nul
if errorlevel 1 (
    echo [AVISO] Instalando dependencias necessarias...
    echo Esta operacao pode demorar alguns minutos...
    echo.
    
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    echo.
    echo [INFO] Verificando instalacao...
    python -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL" 2>nul
    if errorlevel 1 (
        echo [ERRO] Falha na instalacao de dependencias!
        echo.
        echo SOLUCAO MANUAL:
        echo 1. Abra o Prompt de Comando como Administrador
        echo 2. Digite: pip install opencv-python numpy pandas reportlab scikit-learn pillow openpyxl
        echo 3. Execute este arquivo novamente
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Todas as dependencias estao instaladas!
echo.

REM Executar aplicacao
echo [INFO] Iniciando DETFACE Desktop...
echo Aguarde a interface grafica aparecer...
echo.

python detface_desktop.py

REM Verificar se houve erro
if errorlevel 1 (
    echo.
    echo [ERRO] A aplicacao encontrou um problema!
    echo.
    echo DIAGNOSTICO:
    echo 1. Verifique os logs na pasta 'logs'
    echo 2. Certifique-se de que a camera esta conectada (opcional)
    echo 3. Tente executar como Administrador
    echo.
    echo Para mais ajuda, consulte o arquivo README.txt
    echo.
    pause
) else (
    echo.
    echo [INFO] Aplicacao encerrada normalmente.
)

pause
