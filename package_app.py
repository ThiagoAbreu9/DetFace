#!/usr/bin/env python3
"""
Script alternativo para empacotar DETFACE
Cria pacote portátil sem PyInstaller
"""

import os
import shutil
import platform
import zipfile
import json
from datetime import datetime

def get_system_info():
    """Retorna informações do sistema"""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    elif system == 'darwin':
        return 'macos'
    else:
        return 'unknown'

def create_portable_package():
    """Cria pacote portátil da aplicação"""
    system_name = get_system_info()
    package_name = f'DETFACE_Portable_{system_name}'
    
    print(f"📦 Criando pacote portátil para {system_name.upper()}...")
    
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
        else:
            print(f"⚠️ Arquivo não encontrado: {file}")
    
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
    print("⚙️ Copiando configurações...")
    config_files = ['config.json', 'users.json', 'registro_presenca.csv']
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy2(config_file, package_name)
        else:
            # Criar arquivos padrão
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
    
    # Criar script de execução
    create_run_script(package_name, system_name)
    
    # Criar arquivo requirements
    create_requirements_file(package_name)
    
    # Criar README detalhado
    create_detailed_readme(package_name, system_name)
    
    # Criar script de instalação de dependências
    create_install_script(package_name, system_name)
    
    return package_name

def create_run_script(package_name, system_name):
    """Cria script de execução"""
    print("🚀 Criando scripts de execução...")
    
    if system_name == 'windows':
        # Script .bat para Windows
        bat_content = """@echo off
title DETFACE - Sistema de Reconhecimento Facial
echo ========================================
echo      DETFACE - Sistema Iniciando...
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.8+ de python.org
    pause
    exit /b 1
)

REM Verificar dependencias
echo Verificando dependencias...
python -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL" 2>nul
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
)

REM Executar aplicacao
echo Iniciando DETFACE Desktop...
python detface_desktop.py

if errorlevel 1 (
    echo.
    echo ERRO ao executar aplicacao!
    echo Verifique o arquivo logs/detface_%date:~-4,4%-%date:~-10,2%-%date:~-7,2%.log
    pause
)
"""
        
        with open(os.path.join(package_name, 'DETFACE.bat'), 'w', encoding='utf-8') as f:
            f.write(bat_content)
            
        # Script PowerShell alternativo
        ps_content = """# DETFACE - Sistema de Reconhecimento Facial
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "     DETFACE - Sistema Iniciando..." -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
try {
    $pythonVersion = python --version 2>$null
    Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale Python 3.8+ de python.org" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Verificar dependências
Write-Host "Verificando dependências..." -ForegroundColor Yellow
try {
    python -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL" 2>$null
    Write-Host "Dependências OK" -ForegroundColor Green
} catch {
    Write-Host "Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Executar aplicação
Write-Host "Iniciando DETFACE Desktop..." -ForegroundColor Green
python detface_desktop.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO ao executar aplicação!" -ForegroundColor Red
    Write-Host "Verifique os logs na pasta logs/" -ForegroundColor Yellow
    Read-Host "Pressione Enter para sair"
}
"""
        
        with open(os.path.join(package_name, 'DETFACE.ps1'), 'w', encoding='utf-8') as f:
            f.write(ps_content)
    
    elif system_name == 'linux':
        # Script shell para Linux
        sh_content = """#!/bin/bash
# DETFACE - Sistema de Reconhecimento Facial

echo "========================================"
echo "     DETFACE - Sistema Iniciando..."  
echo "========================================"
echo ""

# Cores para output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[0;33m'
CYAN='\\033[0;36m'
NC='\\033[0m' # No Color

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERRO: Python3 não encontrado!${NC}"
    echo -e "${YELLOW}Instale com: sudo apt install python3 python3-pip${NC}"
    exit 1
fi

echo -e "${GREEN}Python encontrado: $(python3 --version)${NC}"

# Verificar dependências
echo -e "${YELLOW}Verificando dependências...${NC}"
if ! python3 -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL" 2>/dev/null; then
    echo -e "${YELLOW}Instalando dependências...${NC}"
    pip3 install -r requirements.txt
    
    # Verificar se ainda falta algo
    if ! python3 -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL" 2>/dev/null; then
        echo -e "${RED}Erro nas dependências. Tente instalar manualmente:${NC}"
        echo -e "${YELLOW}sudo apt install python3-tk python3-opencv${NC}"
        echo -e "${YELLOW}pip3 install -r requirements.txt${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}Dependências OK${NC}"

# Executar aplicação
echo -e "${GREEN}Iniciando DETFACE Desktop...${NC}"
python3 detface_desktop.py

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}ERRO ao executar aplicação!${NC}"
    echo -e "${YELLOW}Verifique os logs na pasta logs/${NC}"
    read -p "Pressione Enter para sair..."
fi
"""
        
        script_path = os.path.join(package_name, 'DETFACE.sh')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(sh_content)
        
        # Tornar executável
        os.chmod(script_path, 0o755)

def create_requirements_file(package_name):
    """Cria arquivo requirements.txt"""
    requirements = """# DETFACE - Dependências Python
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

def create_install_script(package_name, system_name):
    """Cria script de instalação de dependências"""
    print("🔧 Criando scripts de instalação...")
    
    if system_name == 'windows':
        install_content = """@echo off
title DETFACE - Instalador de Dependencias
echo ==========================================
echo   DETFACE - Instalador de Dependencias
echo ==========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo.
    echo Baixe e instale Python de: https://python.org
    echo Certifique-se de marcar "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo Python encontrado!
echo.

REM Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependências
echo Instalando dependencias do DETFACE...
pip install -r requirements.txt

REM Verificar instalação
echo.
echo Verificando instalacao...
python -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL; print('Todas as dependencias instaladas com sucesso!')"

if errorlevel 1 (
    echo.
    echo AVISO: Algumas dependencias podem ter falhado
    echo Tente executar manualmente:
    echo pip install opencv-python numpy pandas reportlab scikit-learn pillow openpyxl
    echo.
) else (
    echo.
    echo ========================================
    echo    INSTALACAO CONCLUIDA COM SUCESSO!
    echo ========================================
    echo.
    echo Agora voce pode executar DETFACE.bat
)

pause
"""
        
        with open(os.path.join(package_name, 'instalar_dependencias.bat'), 'w', encoding='utf-8') as f:
            f.write(install_content)
    
    elif system_name == 'linux':
        install_content = """#!/bin/bash
# DETFACE - Instalador de Dependências Linux

echo "=========================================="
echo "  DETFACE - Instalador de Dependências"
echo "=========================================="
echo ""

# Cores
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[0;33m'
NC='\\033[0m'

# Detectar distribuição
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
fi

echo -e "${YELLOW}Sistema detectado: $OS${NC}"
echo ""

# Instalar dependências do sistema
echo -e "${YELLOW}Instalando dependências do sistema...${NC}"

if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    sudo apt update
    sudo apt install -y python3 python3-pip python3-tk
    sudo apt install -y libopencv-dev python3-opencv
    sudo apt install -y libgl1-mesa-glx libglib2.0-0
    
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Fedora"* ]]; then
    sudo dnf install -y python3 python3-pip tkinter
    sudo dnf install -y opencv-devel python3-opencv
    sudo dnf install -y mesa-libGL glib2
    
elif [[ "$OS" == *"Arch"* ]]; then
    sudo pacman -S python python-pip tk opencv
    sudo pacman -S mesa glib2
    
else
    echo -e "${YELLOW}Distribuição não reconhecida. Instale manualmente:${NC}"
    echo "- python3, python3-pip, python3-tk"
    echo "- opencv, mesa, glib2"
fi

# Instalar dependências Python
echo ""
echo -e "${YELLOW}Instalando dependências Python...${NC}"

# Atualizar pip
python3 -m pip install --upgrade pip

# Instalar requirements
pip3 install -r requirements.txt

# Verificar instalação
echo ""
echo -e "${YELLOW}Verificando instalação...${NC}"

if python3 -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL" 2>/dev/null; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   INSTALAÇÃO CONCLUÍDA COM SUCESSO!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${GREEN}Agora você pode executar: ./DETFACE.sh${NC}"
else
    echo -e "${RED}AVISO: Algumas dependências podem ter falhado${NC}"
    echo -e "${YELLOW}Tente instalar manualmente as dependências em falta${NC}"
fi

echo ""
read -p "Pressione Enter para continuar..."
"""
        
        script_path = os.path.join(package_name, 'instalar_dependencias.sh')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(install_content)
        
        os.chmod(script_path, 0o755)

def create_detailed_readme(package_name, system_name):
    """Cria README detalhado"""
    print("📖 Criando documentação...")
    
    if system_name == 'windows':
        readme_content = """# DETFACE - Sistema de Reconhecimento Facial
Versão Portátil para Windows

## 🚀 INÍCIO RÁPIDO

### Opção 1: Executar Diretamente (Recomendado)
1. Execute `instalar_dependencias.bat` (primeira vez apenas)
2. Execute `DETFACE.bat`
3. A aplicação abrirá automaticamente

### Opção 2: Executar com PowerShell
1. Clique com botão direito no arquivo `DETFACE.ps1`
2. Selecione "Executar com PowerShell"

## 📋 REQUISITOS

### Sistema:
- Windows 10 ou superior (64-bit recomendado)
- 4 GB RAM mínimo
- 500 MB espaço em disco
- Câmera USB ou integrada (opcional)

### Software:
- Python 3.8 ou superior
- Baixe em: https://python.org
- ⚠️ IMPORTANTE: Marque "Add Python to PATH" durante instalação

## 🔧 INSTALAÇÃO

### Primeira Execução:
1. Extraia todos os arquivos para uma pasta permanente
2. Execute `instalar_dependencias.bat`
3. Aguarde a instalação das dependências
4. Execute `DETFACE.bat`

### Se der erro:
```bat
# Instalar manualmente
pip install opencv-python numpy pandas reportlab scikit-learn pillow openpyxl
```

## 💡 COMO USAR

### Interface Principal:
- **🎯 Reconhecimento**: Identifica pessoas em tempo real
- **👤 Cadastrar**: Registra novos usuários no sistema
- **🔧 Administração**: Gerencia usuários cadastrados  
- **📊 Relatórios**: Gera relatórios de presença

### Primeiros Passos:
1. Conecte uma câmera (se disponível)
2. Vá para aba "Cadastrar Usuário"
3. Preencha os dados e capture uma foto
4. Use a aba "Reconhecimento" para identificar pessoas

### Sem Câmera:
- O sistema funciona normalmente
- Use modo demo para testar funcionalidades
- Cadastre usuários manualmente

## 🗂️ ESTRUTURA DE ARQUIVOS

```
DETFACE_Portable_windows/
├── DETFACE.bat                 # Executar aplicação
├── DETFACE.ps1                 # Alternativa PowerShell
├── instalar_dependencias.bat   # Instalar requisitos
├── requirements.txt            # Lista de dependências
├── README.txt                  # Este arquivo
├── detface_desktop.py          # Aplicação principal
├── face_detector.py           # Motor de reconhecimento
├── user_manager.py            # Gerenciamento de usuários
├── report_generator.py        # Gerador de relatórios
├── config.json                # Configurações
├── users.json                 # Banco de usuários
├── faces/                     # Fotos dos usuários
├── logs/                      # Logs do sistema
├── reports/                   # Relatórios gerados
└── backup/                    # Backups automáticos
```

## ⚠️ SOLUÇÃO DE PROBLEMAS

### "Python não encontrado":
- Instale Python de python.org
- Certifique-se de marcar "Add Python to PATH"
- Reinicie o computador após instalação

### "Erro MSVCP140.dll":
- Baixe Visual C++ Redistributable:
  https://aka.ms/vs/17/release/vc_redist.x64.exe

### Câmera não funciona:
- Verifique se está conectada
- Teste em outro aplicativo (Câmera do Windows)
- Reinstale drivers se necessário
- Sistema funciona sem câmera em modo demo

### Aplicação não abre:
- Execute como administrador
- Verifique antivírus/Windows Defender  
- Consulte logs na pasta logs/
- Tente executar: `python detface_desktop.py`

### Erro de dependências:
- Execute `instalar_dependencias.bat` novamente
- Ou instale manualmente:
  ```
  pip install opencv-python numpy pandas reportlab scikit-learn pillow openpyxl
  ```

## 🔒 SEGURANÇA E PRIVACIDADE

- Todos os dados ficam armazenados localmente
- Nenhuma informação é enviada para internet
- Faça backup regular da pasta inteira
- As fotos ficam apenas na pasta faces/

## 📞 SUPORTE

### Auto-diagnóstico:
1. Verifique logs em logs/
2. Execute `python --version`
3. Execute `pip list` para ver dependências
4. Teste: `python -c "import cv2, tkinter"`

### Logs importantes:
- logs/detface_YYYY-MM-DD.log
- Erros aparecem no console

## 🚀 DISTRIBUIÇÃO

Esta é uma versão portátil que pode ser:
- Copiada para qualquer computador Windows
- Executada de pen drive (se Python estiver instalado)
- Distribuída sem instalação complexa

Para usar em outro PC:
1. Copie a pasta inteira
2. Instale Python no PC de destino
3. Execute `instalar_dependencias.bat`
4. Execute `DETFACE.bat`
"""

    elif system_name == 'linux':
        readme_content = """# DETFACE - Sistema de Reconhecimento Facial
Versão Portátil para Linux

## 🚀 INÍCIO RÁPIDO

### Método Simples:
```bash
# Tornar executável
chmod +x DETFACE.sh instalar_dependencias.sh

# Instalar dependências (primeira vez)
./instalar_dependencias.sh

# Executar aplicação
./DETFACE.sh
```

### Método Manual:
```bash
# Instalar dependências Python
pip3 install -r requirements.txt

# Executar aplicação
python3 detface_desktop.py
```

## 📋 REQUISITOS

### Sistema:
- Linux com kernel 3.10+ (Ubuntu 18.04+, CentOS 7+)
- 4 GB RAM mínimo
- 500 MB espaço em disco
- Interface gráfica (X11 ou Wayland)
- Câmera V4L2 compatível (opcional)

### Software:
- Python 3.8+
- pip3
- tkinter
- Dependências de desenvolvimento

## 🔧 INSTALAÇÃO

### Ubuntu/Debian:
```bash
# Dependências do sistema
sudo apt update
sudo apt install -y python3 python3-pip python3-tk
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y libgl1-mesa-glx libglib2.0-0

# Dependências Python
pip3 install -r requirements.txt

# Executar
./DETFACE.sh
```

### CentOS/RHEL/Fedora:
```bash
# Dependências do sistema  
sudo dnf install -y python3 python3-pip tkinter
sudo dnf install -y opencv-devel python3-opencv
sudo dnf install -y mesa-libGL glib2

# Dependências Python
pip3 install -r requirements.txt

# Executar
./DETFACE.sh
```

### Arch Linux:
```bash
# Dependências do sistema
sudo pacman -S python python-pip tk opencv
sudo pacman -S mesa glib2

# Dependências Python
pip3 install -r requirements.txt

# Executar
./DETFACE.sh
```

## 💡 COMO USAR

### Interface Principal:
- **🎯 Reconhecimento**: Identifica pessoas em tempo real
- **👤 Cadastrar**: Registra novos usuários no sistema
- **🔧 Administração**: Gerencia usuários cadastrados
- **📊 Relatórios**: Gera relatórios de presença

### Primeiros Passos:
1. Conecte uma câmera USB
2. Vá para aba "Cadastrar Usuário"
3. Preencha os dados e capture uma foto  
4. Use a aba "Reconhecimento" para identificar pessoas

### Sem Câmera:
- O sistema funciona em modo demo
- Cadastre usuários manualmente
- Teste todas as funcionalidades

## 🗂️ ESTRUTURA DE ARQUIVOS

```
DETFACE_Portable_linux/
├── DETFACE.sh                 # Executar aplicação
├── instalar_dependencias.sh   # Instalar requisitos
├── requirements.txt           # Lista de dependências
├── README.txt                 # Este arquivo
├── detface_desktop.py         # Aplicação principal
├── face_detector.py          # Motor de reconhecimento
├── user_manager.py           # Gerenciamento de usuários
├── report_generator.py       # Gerador de relatórios
├── config.json               # Configurações
├── users.json                # Banco de usuários
├── faces/                    # Fotos dos usuários
├── logs/                     # Logs do sistema
├── reports/                  # Relatórios gerados
└── backup/                   # Backups automáticos
```

## ⚠️ SOLUÇÃO DE PROBLEMAS

### "No module named 'tkinter'":
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL
sudo dnf install tkinter

# Arch
sudo pacman -S tk
```

### Câmera não funciona:
```bash
# Verificar câmeras disponíveis
ls /dev/video*

# Testar câmera
sudo apt install cheese
cheese

# Permissões de câmera
sudo usermod -a -G video $USER
# Reiniciar sessão após comando acima
```

### Erro de permissões:
```bash
# Dar permissão de execução
chmod +x DETFACE.sh

# Verificar propriedade dos arquivos
ls -la faces/ logs/ reports/
```

### Interface não aparece:
```bash
# Verificar display
echo $DISPLAY

# Para SSH com X11:
ssh -X usuario@servidor
./DETFACE.sh

# Para Wayland:
export QT_QPA_PLATFORM=wayland
./DETFACE.sh
```

### Dependências em falta:
```bash
# Verificar dependências Python
python3 -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL"

# Verificar bibliotecas do sistema
ldd $(which python3)

# Instalar dependências em falta
sudo apt install libgl1-mesa-glx libglib2.0-0
```

## 🔒 SEGURANÇA E PRIVACIDADE

- Todos os dados ficam armazenados localmente
- Nenhuma informação é enviada para internet
- Backup automático disponível

### Backup manual:
```bash
# Backup completo
tar -czf detface_backup_$(date +%Y%m%d).tar.gz \\
    faces/ logs/ reports/ config.json users.json

# Restaurar backup
tar -xzf detface_backup_YYYYMMDD.tar.gz
```

## 📞 SUPORTE

### Auto-diagnóstico:
```bash
# Verificar Python
python3 --version

# Verificar dependências
pip3 list | grep -E "(opencv|numpy|pandas|reportlab|scikit-learn|pillow)"

# Testar importações
python3 -c "import cv2, tkinter, numpy, pandas, reportlab, sklearn, PIL; print('OK')"

# Verificar logs
cat logs/detface_$(date +%Y-%m-%d).log

# Modo debug
python3 detface_desktop.py --debug
```

### Permissões de câmera:
```bash
# Verificar grupos do usuário
groups $USER

# Adicionar ao grupo video se necessário
sudo usermod -a -G video $USER

# Verificar permissões da câmera
ls -l /dev/video*
```

## 🚀 DISTRIBUIÇÃO

Esta versão portátil pode ser:
- Copiada para qualquer sistema Linux
- Executada de dispositivos removíveis
- Distribuída sem instalação complexa

### Para usar em outro PC Linux:
1. Copie a pasta inteira
2. Execute `./instalar_dependencias.sh`
3. Execute `./DETFACE.sh`

### Criar .desktop para menu:
```bash
cat > ~/.local/share/applications/detface.desktop << EOF
[Desktop Entry]
Name=DETFACE
Comment=Sistema de Reconhecimento Facial
Exec=/caminho/completo/para/DETFACE.sh
Icon=camera
Terminal=false
Type=Application
Categories=Office;Photography;Security;
EOF
```
"""

    with open(os.path.join(package_name, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

def create_zip_package(package_name):
    """Cria arquivo ZIP do pacote"""
    print("📦 Criando arquivo ZIP...")
    
    zip_name = f"{package_name}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_name):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, package_name)
                zipf.write(file_path, arc_name)
    
    return zip_name

def main():
    system_name = get_system_info()
    
    print("📦 DETFACE - Criador de Pacote Portátil")
    print("=" * 50)
    print(f"🖥️ Sistema: {system_name.upper()}")
    print()
    
    # Verificar arquivos necessários
    required_files = ['detface_desktop.py', 'face_detector.py', 'user_manager.py', 'report_generator.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Arquivos não encontrados: {missing_files}")
        return False
    
    # Criar pacote
    package_name = create_portable_package()
    
    # Criar ZIP
    zip_file = create_zip_package(package_name)
    
    # Obter tamanhos
    package_size = sum(os.path.getsize(os.path.join(package_name, f)) 
                      for f in os.listdir(package_name) 
                      if os.path.isfile(os.path.join(package_name, f))) / (1024 * 1024)
    
    zip_size = os.path.getsize(zip_file) / (1024 * 1024)
    
    print("\n" + "=" * 50)
    print("🎉 PACOTE CRIADO COM SUCESSO!")
    print("=" * 50)
    print(f"📁 Pasta: {package_name}/")
    print(f"📦 ZIP: {zip_file}")
    print(f"📊 Tamanho pasta: {package_size:.1f} MB")
    print(f"📊 Tamanho ZIP: {zip_size:.1f} MB")
    print()
    
    if system_name == 'windows':
        print("🪟 Para Windows:")
        print(f"   1. Extraia {zip_file}")
        print("   2. Execute instalar_dependencias.bat")
        print("   3. Execute DETFACE.bat")
    elif system_name == 'linux':
        print("🐧 Para Linux:")
        print(f"   1. Extraia {zip_file}")
        print("   2. chmod +x *.sh")
        print("   3. ./instalar_dependencias.sh")
        print("   4. ./DETFACE.sh")
    
    print("\n📖 Leia README.txt para instruções detalhadas")
    print("✅ Pronto para distribuir!")
    
    return True

if __name__ == "__main__":
    main()