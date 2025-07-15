@echo off
title DETFACE - Executor de Testes
color 0A
echo.
echo ===============================================
echo    DETFACE - Executor de Testes Automatizados
echo ===============================================
echo.

REM Verificar se pytest está instalado
echo [1/3] Verificando pytest...
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo [INFO] Instalando pytest...
    pip install pytest
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar pytest
        pause
        exit /b 1
    )
)

echo [OK] pytest encontrado!
echo.

REM Verificar dependências de teste
echo [2/3] Verificando dependências de teste...
python -c "import tempfile, shutil, pathlib, pandas, numpy, cv2" 2>nul
if errorlevel 1 (
    echo [ERRO] Algumas dependências de teste não estão instaladas
    echo Execute: pip install pytest pandas numpy opencv-python
    pause
    exit /b 1
)

echo [OK] Dependências de teste encontradas!
echo.

REM Executar testes
echo [3/3] Executando testes...
echo.

echo OPÇÕES DE TESTE:
echo 1. Todos os testes
echo 2. Apenas testes unitários
echo 3. Apenas testes de integração
echo 4. Apenas testes de performance
echo 5. Testes específicos
echo.

set /p choice="Escolha uma opção (1-5): "

if "%choice%"=="1" (
    echo Executando todos os testes...
    python -m pytest test_detface.py -v
) else if "%choice%"=="2" (
    echo Executando testes unitários...
    python -m pytest test_detface.py -v -m "unit"
) else if "%choice%"=="3" (
    echo Executando testes de integração...
    python -m pytest test_detface.py -v -m "integration"
) else if "%choice%"=="4" (
    echo Executando testes de performance...
    python -m pytest test_detface.py -v -m "performance"
) else if "%choice%"=="5" (
    echo.
    echo Testes disponíveis:
    echo - test_01_system_initialization
    echo - test_02_user_manager_initialization
    echo - test_03_face_detector_initialization
    echo - test_04_report_generator_initialization
    echo - test_05_add_user_success
    echo - test_06_add_user_duplicate
    echo - test_07_remove_user_success
    echo - test_08_remove_user_not_found
    echo - test_09_update_user
    echo - test_10_get_all_users
    echo - test_11_get_active_users
    echo - test_12_validate_user_data
    echo - test_13_search_users
    echo - test_14_face_detection_initialization
    echo - test_15_face_feature_extraction
    echo - test_16_camera_check
    echo - test_17_report_generation_csv
    echo - test_18_report_statistics
    echo - test_19_user_statistics_update
    echo - test_20_config_file_operations
    echo.
    set /p test_name="Digite o nome do teste (ex: test_05_add_user_success): "
    python -m pytest test_detface.py::TestDetfaceSystem::%test_name% -v
) else (
    echo Opção inválida!
    pause
    exit /b 1
)

echo.
echo ===============================================
echo              TESTES CONCLUÍDOS
echo ===============================================
echo.
echo Para ver relatório detalhado:
echo python -m pytest test_detface.py -v --tb=long
echo.
echo Para executar testes específicos:
echo python -m pytest test_detface.py::TestDetfaceSystem::test_XX_ -v
echo.
pause 