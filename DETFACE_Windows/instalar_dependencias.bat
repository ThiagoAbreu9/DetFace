@echo off
title DETFACE - Instalador de Dependencias
color 0B
echo.
echo ===============================================
echo    DETFACE - Instalador de Dependencias
echo ===============================================
echo.

REM Verificar se Python esta instalado
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo INSTRUCOES PARA INSTALAR PYTHON:
    echo 1. Va para: https://python.org/downloads/
    echo 2. Baixe Python 3.8 ou superior
    echo 3. Durante a instalacao:
    echo    - Marque "Add Python to PATH"
    echo    - Marque "Install for all users"
    echo 4. Reinicie o computador
    echo 5. Execute este arquivo novamente
    echo.
    start https://python.org/downloads/
    pause
    exit /b 1
)

python --version
echo [OK] Python encontrado!
echo.

REM Verificar pip
echo [2/4] Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] pip nao encontrado!
    echo Reinstale o Python marcando "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] pip encontrado!
echo.

REM Atualizar pip
echo [3/4] Atualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependencias
echo [4/4] Instalando dependencias do DETFACE...
echo Esta operacao pode demorar 5-10 minutos dependendo da sua conexao...
echo.

pip install opencv-python
if errorlevel 1 goto erro_instalacao

pip install numpy
if errorlevel 1 goto erro_instalacao

pip install pandas  
if errorlevel 1 goto erro_instalacao

pip install reportlab
if errorlevel 1 goto erro_instalacao

pip install scikit-learn
if errorlevel 1 goto erro_instalacao

pip install pillow
if errorlevel 1 goto erro_instalacao

pip install openpyxl
if errorlevel 1 goto erro_instalacao

echo.
echo [INFO] Testando instalacao...
python -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL; print('SUCESSO: Todas as dependencias foram instaladas!')"

if errorlevel 1 (
    echo [ERRO] Algumas dependencias falharam no teste!
    goto erro_instalacao
)

echo.
echo ===============================================
echo        INSTALACAO CONCLUIDA COM SUCESSO!
echo ===============================================
echo.
echo Agora voce pode:
echo 1. Fechar esta janela
echo 2. Executar o arquivo "DETFACE.bat"
echo 3. Usar o sistema normalmente
echo.
echo A aplicacao ira abrir em uma nova janela.
echo.
pause
exit /b 0

:erro_instalacao
echo.
echo ===============================================
echo              ERRO NA INSTALACAO
echo ===============================================
echo.
echo SOLUCOES POSSIVEIS:
echo.
echo 1. VERIFICAR CONEXAO COM INTERNET:
echo    - Certifique-se de estar conectado
echo    - Desative antivirus temporariamente
echo.
echo 2. EXECUTAR COMO ADMINISTRADOR:
echo    - Clique com botao direito neste arquivo
echo    - Selecione "Executar como administrador"
echo.
echo 3. INSTALAR MANUALMENTE:
echo    - Abra o Prompt de Comando como Administrador
echo    - Digite: pip install -r requirements.txt
echo.
echo 4. VERIFICAR FIREWALL/PROXY:
echo    - Configure proxy se necessario
echo    - Libere acesso ao pip no firewall
echo.
pause
exit /b 1
