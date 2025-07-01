#!/usr/bin/env python3
"""
Criador de pacote Windows para DETFACE
"""

import os
import shutil
import zipfile
import json

def create_windows_package():
    """Cria pacote específico para Windows"""
    package_name = 'DETFACE_Windows'
    
    print("🪟 Criando pacote para Windows...")
    
    # Criar pasta do pacote
    if os.path.exists(package_name):
        shutil.rmtree(package_name)
    os.makedirs(package_name)
    
    # Arquivos Python necessários
    python_files = [
        'detface_desktop.py',
        'face_detector.py', 
        'user_manager.py',
        'report_generator.py',
        'web_camera.py',
        'main.py'
    ]
    
    # Copiar arquivos Python
    print("📄 Copiando arquivos Python...")
    for file in python_files:
        if os.path.exists(file):
            shutil.copy2(file, package_name)
    
    # Copiar pastas necessárias
    print("📁 Copiando pastas...")
    folders = ['faces', 'templates', 'logs', 'reports', 'backup']
    for folder in folders:
        dest_folder = os.path.join(package_name, folder)
        if os.path.exists(folder):
            shutil.copytree(folder, dest_folder, dirs_exist_ok=True)
        else:
            os.makedirs(dest_folder)
            with open(os.path.join(dest_folder, '.gitkeep'), 'w') as f:
                f.write('')
    
    # Copiar arquivos de configuração
    config_files = ['config.json', 'users.json', 'registro_presenca.csv']
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy2(config_file, package_name)
        else:
            if config_file == 'config.json':
                default_config = {
                    "camera_index": 0,
                    "recognition_threshold": 0.7,
                    "recognition_cooldown": 5,
                    "max_faces": 10,
                    "auto_backup": True,
                    "backup_interval": 7,
                    "log_level": "INFO"
                }
                with open(os.path.join(package_name, config_file), 'w') as f:
                    json.dump(default_config, f, indent=2)
            elif config_file == 'users.json':
                with open(os.path.join(package_name, config_file), 'w') as f:
                    f.write('{}')
            elif config_file == 'registro_presenca.csv':
                with open(os.path.join(package_name, config_file), 'w') as f:
                    f.write('timestamp,user_id,name,type\n')
    
    # Criar scripts Windows
    create_windows_scripts(package_name)
    create_windows_readme(package_name)
    create_requirements_file(package_name)
    
    return package_name

def create_windows_scripts(package_name):
    """Cria scripts específicos para Windows"""
    
    # Script principal .bat
    main_bat = """@echo off
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
"""
    
    with open(os.path.join(package_name, 'DETFACE.bat'), 'w', encoding='utf-8') as f:
        f.write(main_bat)
    
    # Script de instalação de dependências
    install_bat = """@echo off
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
"""
    
    with open(os.path.join(package_name, 'instalar_dependencias.bat'), 'w', encoding='utf-8') as f:
        f.write(install_bat)
    
    # Script PowerShell alternativo
    ps_script = """# DETFACE - PowerShell Launcher
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
"""
    
    with open(os.path.join(package_name, 'DETFACE.ps1'), 'w', encoding='utf-8') as f:
        f.write(ps_script)

def create_requirements_file(package_name):
    """Cria arquivo requirements.txt para Windows"""
    requirements = """# DETFACE - Dependências Windows
opencv-python>=4.5.0
numpy>=1.21.0
pandas>=1.3.0
reportlab>=3.6.0
scikit-learn>=1.0.0
Pillow>=8.3.0
openpyxl>=3.0.0
"""
    
    with open(os.path.join(package_name, 'requirements.txt'), 'w') as f:
        f.write(requirements)

def create_windows_readme(package_name):
    """Cria README específico para Windows"""
    
    readme_content = """# DETFACE - Sistema de Reconhecimento Facial
## Versão para Windows

### 🚀 COMO USAR (MÉTODO MAIS FÁCIL)

1. **BAIXE E INSTALE O PYTHON:**
   - Vá em: https://python.org/downloads/
   - Baixe Python 3.8 ou superior
   - ⚠️ IMPORTANTE: Marque "Add Python to PATH" durante a instalação
   - Reinicie o computador após instalar

2. **INSTALE AS DEPENDÊNCIAS:**
   - Execute o arquivo: `instalar_dependencias.bat`
   - Aguarde a instalação (pode demorar 5-10 minutos)

3. **EXECUTE O PROGRAMA:**
   - Execute o arquivo: `DETFACE.bat`
   - A aplicação abrirá em uma nova janela

### 📋 REQUISITOS DO SISTEMA

- Windows 10 ou superior (64-bit recomendado)
- 4 GB RAM mínimo
- 500 MB espaço em disco
- Conexão com internet (para instalar dependências)
- Câmera USB ou integrada (opcional)

### 🎯 FUNCIONALIDADES

**Interface com 4 abas:**
- 🎯 **Reconhecimento**: Identifica pessoas em tempo real
- 👤 **Cadastrar**: Registra novos usuários
- 🔧 **Administração**: Gerencia usuários cadastrados
- 📊 **Relatórios**: Gera relatórios de presença

### 📁 ARQUIVOS IMPORTANTES

```
DETFACE_Windows/
├── DETFACE.bat                 ← EXECUTE ESTE ARQUIVO
├── instalar_dependencias.bat   ← Execute primeiro (só uma vez)
├── DETFACE.ps1                 ← Alternativa PowerShell
├── README.txt                  ← Este arquivo
├── requirements.txt            ← Lista de dependências
├── detface_desktop.py          ← Aplicação principal
├── face_detector.py           ← Reconhecimento facial
├── user_manager.py            ← Gerencia usuários
├── report_generator.py        ← Gera relatórios
├── config.json                ← Configurações
├── users.json                 ← Dados dos usuários
├── faces/                     ← Fotos dos usuários
├── logs/                      ← Logs do sistema
├── reports/                   ← Relatórios gerados
└── backup/                    ← Backups automáticos
```

### 🔧 MÉTODOS DE EXECUÇÃO

**Método 1 - Arquivo .bat (Recomendado):**
- Clique duas vezes em `DETFACE.bat`

**Método 2 - PowerShell:**
- Clique com botão direito em `DETFACE.ps1`
- Selecione "Executar com PowerShell"

**Método 3 - Manual:**
- Abra o Prompt de Comando nesta pasta
- Digite: `python detface_desktop.py`

### ⚠️ SOLUÇÃO DE PROBLEMAS

#### "Python não encontrado"
**CAUSA:** Python não instalado ou não está no PATH
**SOLUÇÃO:**
1. Baixe Python de: https://python.org/downloads/
2. Durante instalação, marque "Add Python to PATH"
3. Reinicie o computador
4. Execute `DETFACE.bat` novamente

#### "Erro MSVCP140.dll não encontrado"
**CAUSA:** Visual C++ Redistributable não instalado
**SOLUÇÃO:**
- Baixe e instale: https://aka.ms/vs/17/release/vc_redist.x64.exe

#### "Erro ao instalar dependências"
**POSSÍVEIS CAUSAS:**
- Sem conexão com internet
- Firewall/antivírus bloqueando
- Falta de permissões

**SOLUÇÕES:**
1. Execute como Administrador (clique direito → "Executar como administrador")
2. Desative antivírus temporariamente
3. Verifique conexão com internet
4. Execute: `instalar_dependencias.bat` como administrador

#### "Câmera não funciona"
**O sistema funciona sem câmera!**
- Use modo DEMO para testar
- Cadastre usuários manualmente
- Verifique se câmera está conectada
- Teste câmera no aplicativo "Câmera" do Windows

#### "Aplicação não abre"
**DIAGNÓSTICO:**
1. Verifique logs na pasta `logs/`
2. Execute pelo Prompt de Comando para ver erros
3. Tente executar como Administrador
4. Verifique se Windows Defender está bloqueando

**COMANDOS DE TESTE:**
```cmd
python --version
python -c "import cv2, tkinter"
python detface_desktop.py
```

### 🔒 SEGURANÇA E PRIVACIDADE

- ✅ Todos os dados ficam no seu computador
- ✅ Nenhuma informação é enviada para internet
- ✅ Sistema funciona offline (após instalação)
- ✅ Você controla todos os dados

**BACKUP DOS DADOS:**
- Copie a pasta inteira para backup
- Dados importantes: `faces/`, `users.json`, `config.json`
- Relatórios ficam na pasta `reports/`

### 📞 SUPORTE TÉCNICO

#### Auto-diagnóstico:
1. Abra Prompt de Comando nesta pasta
2. Digite: `python --version` (deve mostrar versão)
3. Digite: `pip list` (deve mostrar bibliotecas instaladas)
4. Digite: `python detface_desktop.py` (deve abrir aplicação)

#### Logs do sistema:
- Verifique arquivos na pasta `logs/`
- Procure por mensagens de erro
- Data/hora dos problemas

#### Teste de câmera:
- Abra aplicativo "Câmera" do Windows
- Se não funcionar lá, problema é no driver
- Sistema DETFACE funciona sem câmera

### 🎮 MODO DEMO (SEM CÂMERA)

Se não tiver câmera, o sistema funciona normalmente:
- Cadastre usuários sem foto
- Teste interface completa
- Gere relatórios
- Configure sistema

### 🚀 DISTRIBUIÇÃO

**Para instalar em outro computador:**
1. Copie a pasta `DETFACE_Windows` inteira
2. No novo PC, instale Python (https://python.org)
3. Execute `instalar_dependencias.bat`
4. Execute `DETFACE.bat`

**Para pen drive/rede:**
- Sistema é totalmente portátil
- Apenas Python precisa estar instalado
- Dados ficam na pasta local

### 📧 INFORMAÇÕES TÉCNICAS

- **Linguagem:** Python 3.8+
- **Interface:** tkinter (nativo do Windows)
- **Reconhecimento:** OpenCV
- **Relatórios:** ReportLab (PDF) + openpyxl (Excel)
- **Armazenamento:** Arquivos locais (JSON/CSV)

Este é um sistema completo e profissional, sem necessidade de servidor ou internet para funcionar!
"""

    with open(os.path.join(package_name, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

def create_zip(package_name):
    """Cria arquivo ZIP"""
    zip_name = f"{package_name}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_name):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, package_name)
                zipf.write(file_path, arc_name)
    return zip_name

def main():
    print("🪟 DETFACE - Criador de Pacote Windows")
    print("=" * 50)
    
    package_name = create_windows_package()
    zip_file = create_zip(package_name)
    
    # Calcular tamanhos
    zip_size = os.path.getsize(zip_file) / (1024 * 1024)
    
    print("\n" + "=" * 50)
    print("🎉 PACOTE WINDOWS CRIADO!")
    print("=" * 50)
    print(f"📁 Pasta: {package_name}/")
    print(f"📦 ZIP: {zip_file}")
    print(f"📊 Tamanho: {zip_size:.1f} MB")
    print()
    print("🪟 INSTRUÇÕES PARA WINDOWS:")
    print("1. Baixe o arquivo ZIP")
    print("2. Extraia para uma pasta")
    print("3. Instale Python de python.org (marque 'Add to PATH')")
    print("4. Execute 'instalar_dependencias.bat'")
    print("5. Execute 'DETFACE.bat'")
    print()
    print("📖 Leia README.txt para instruções completas")
    print("✅ Pronto para usar no Windows!")

if __name__ == "__main__":
    main()