#!/usr/bin/env python3
"""
Script para criar executável do DETFACE
Compatível com Windows e Linux
"""

import subprocess
import sys
import os
import shutil
import platform

def create_spec_file():
    """Cria arquivo de especificação do PyInstaller"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['detface_desktop.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('faces', 'faces'),
        ('templates', 'templates'),
        ('config.json', '.'),
        ('users.json', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'PIL._tkinter_finder',
        'cv2',
        'numpy',
        'sklearn',
        'sklearn.metrics',
        'sklearn.metrics.pairwise',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.platypus',
        'pandas',
        'openpyxl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DETFACE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
    
    with open('detface.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Arquivo de especificação criado")

def get_system_info():
    """Retorna informações do sistema"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == 'windows':
        return 'windows', '.exe'
    elif system == 'linux':
        return 'linux', ''
    elif system == 'darwin':
        return 'macos', ''
    else:
        return 'unknown', ''

def build_executable():
    """Compila o executável para o sistema atual"""
    system_name, ext = get_system_info()
    executable_name = f'DETFACE{ext}'
    
    print(f"🔨 Compilando para {system_name.upper()}...")
    print(f"📁 Executável: {executable_name}")
    
    try:
        # Preparar dados para diferentes sistemas
        if system_name == 'windows':
            data_separator = ';'
        else:
            data_separator = ':'
            
        # Comandos do PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed' if system_name == 'windows' else '--noconsole',
            f'--name={executable_name.replace(ext, "")}',
            f'--add-data=faces{data_separator}faces',
            f'--add-data=templates{data_separator}templates', 
            f'--add-data=config.json{data_separator}.',
            f'--add-data=users.json{data_separator}.',
            '--hidden-import=tkinter',
            '--hidden-import=tkinter.ttk',
            '--hidden-import=PIL._tkinter_finder',
            '--hidden-import=sklearn.metrics.pairwise',
            '--hidden-import=reportlab.pdfgen',
            '--clean',
            'detface_desktop.py'
        ]
        
        # Executar PyInstaller
        print("⚙️ Executando PyInstaller...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Compilação concluída!")
            
            # Verificar se arquivo foi criado
            exe_path = os.path.join('dist', executable_name)
            if os.path.exists(exe_path):
                file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
                print(f"📁 Arquivo: {exe_path}")
                print(f"📊 Tamanho: {file_size:.1f} MB")
                
                # Criar pasta de distribuição
                dist_folder = f'DETFACE_Distribution_{system_name}'
                if os.path.exists(dist_folder):
                    shutil.rmtree(dist_folder)
                os.makedirs(dist_folder)
                
                # Copiar executável
                shutil.copy2(exe_path, os.path.join(dist_folder, executable_name))
                
                # Tornar executável no Linux/Mac
                if system_name in ['linux', 'macos']:
                    os.chmod(os.path.join(dist_folder, executable_name), 0o755)
                
                # Copiar pastas necessárias
                for folder in ['faces', 'templates', 'logs', 'reports', 'backup']:
                    if os.path.exists(folder):
                        shutil.copytree(folder, os.path.join(dist_folder, folder), dirs_exist_ok=True)
                    else:
                        os.makedirs(os.path.join(dist_folder, folder))
                        with open(os.path.join(dist_folder, folder, '.gitkeep'), 'w') as f:
                            f.write('')
                
                # Copiar arquivos de configuração
                for file in ['config.json', 'users.json']:
                    if os.path.exists(file):
                        shutil.copy2(file, dist_folder)
                
                # Criar README específico do sistema
                create_readme(dist_folder, system_name, executable_name)
                
                # Criar script de instalação para Linux
                if system_name == 'linux':
                    create_linux_installer(dist_folder, executable_name)
                
                print(f"📦 Pacote completo: {dist_folder}/")
                print(f"🚀 Execute: {dist_folder}/{executable_name}")
                
                return True, dist_folder
            else:
                print("❌ Arquivo executável não encontrado")
                return False, None
        else:
            print("❌ Erro na compilação:")
            print(result.stderr)
            return False, None
            
    except Exception as e:
        print(f"❌ Erro durante compilação: {e}")
        return False, None

def create_readme(dist_folder, system_name, executable_name):
    """Cria README específico para o sistema"""
    
    readme_content = ""
    
    if system_name == 'windows':
        readme_content = """# DETFACE - Sistema de Reconhecimento Facial

## INSTALAÇÃO - WINDOWS

### Método 1: Executável Portátil (Recomendado)
1. Extraia todos os arquivos desta pasta para um local permanente
2. Execute DETFACE.exe
3. A aplicação abrirá automaticamente

### Método 2: Instalação no Sistema
1. Copie a pasta inteira para C:\\Program Files\\DETFACE\\
2. Crie um atalho do DETFACE.exe na área de trabalho
3. Execute como administrador na primeira vez

## COMO USAR

### Interface Principal:
- 🎯 Reconhecimento: Identifica pessoas em tempo real
- 👤 Cadastrar: Registra novos usuários no sistema  
- 🔧 Administração: Gerencia usuários cadastrados
- 📊 Relatórios: Gera relatórios de presença

### Primeiros Passos:
1. Conecte uma câmera USB ou use a câmera integrada
2. Vá para aba "Cadastrar Usuário"
3. Preencha os dados e capture uma foto
4. Use a aba "Reconhecimento" para identificar pessoas

## REQUISITOS

- Windows 10 ou superior (64-bit)
- 4 GB RAM mínimo (8 GB recomendado)
- Câmera USB ou integrada (opcional)
- 500 MB espaço em disco

## SOLUÇÃO DE PROBLEMAS

### Erro "MSVCP140.dll não encontrado":
- Instale o Visual C++ Redistributable:
  https://aka.ms/vs/17/release/vc_redist.x64.exe

### Câmera não funciona:
- Verifique se a câmera está conectada
- Teste a câmera em outro aplicativo
- Reinstale os drivers da câmera

### Aplicação não abre:
- Execute como administrador
- Verifique o Windows Defender/Antivírus
- Consulte logs na pasta logs/

## ESTRUTURA DE PASTAS

- faces/: Fotos dos usuários cadastrados
- logs/: Registros do sistema
- reports/: Relatórios gerados  
- backup/: Backups automáticos
- config.json: Configurações do sistema
- users.json: Dados dos usuários

## BACKUP E SEGURANÇA

- Faça backup regular da pasta inteira
- Os dados ficam armazenados localmente
- Não são enviadas informações para internet

## SUPORTE

Em caso de problemas:
1. Verifique os logs na pasta logs/
2. Consulte este README
3. Tente executar como administrador
"""
    
    elif system_name == 'linux':
        readme_content = """# DETFACE - Sistema de Reconhecimento Facial

## INSTALAÇÃO - LINUX

### Método 1: Executável Portátil (Recomendado)
```bash
# Tornar executável
chmod +x DETFACE

# Executar
./DETFACE
```

### Método 2: Instalação no Sistema
```bash
# Executar o instalador
sudo ./install.sh

# Ou instalar manualmente:
sudo cp DETFACE /usr/local/bin/
sudo chmod +x /usr/local/bin/DETFACE
detface  # Executar de qualquer local
```

### Método 3: Criar .desktop
```bash
# Criar atalho para menu de aplicações
cat > ~/.local/share/applications/detface.desktop << EOF
[Desktop Entry]
Name=DETFACE
Comment=Sistema de Reconhecimento Facial
Exec=/caminho/para/DETFACE
Icon=camera
Terminal=false
Type=Application
Categories=Office;Photography;
EOF
```

## DEPENDÊNCIAS

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y python3-tk libopencv-dev
sudo apt install -y libgl1-mesa-glx libglib2.0-0
```

### CentOS/RHEL/Fedora:
```bash
sudo dnf install -y tkinter opencv-devel
sudo dnf install -y mesa-libGL glib2
```

### Arch Linux:
```bash
sudo pacman -S tk opencv
sudo pacman -S mesa glib2
```

## COMO USAR

### Interface Principal:
- 🎯 Reconhecimento: Identifica pessoas em tempo real
- 👤 Cadastrar: Registra novos usuários no sistema  
- 🔧 Administração: Gerencia usuários cadastrados
- 📊 Relatórios: Gera relatórios de presença

### Primeiros Passos:
1. Conecte uma câmera USB ou use a câmera integrada
2. Vá para aba "Cadastrar Usuário"  
3. Preencha os dados e capture uma foto
4. Use a aba "Reconhecimento" para identificar pessoas

## REQUISITOS

- Linux com kernel 3.10+ (Ubuntu 18.04+, CentOS 7+)
- 4 GB RAM mínimo (8 GB recomendado)
- Câmera V4L2 compatível (opcional)
- 500 MB espaço em disco
- Interface gráfica (X11 ou Wayland)

## SOLUÇÃO DE PROBLEMAS

### Erro "No module named 'tkinter'":
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# CentOS/RHEL  
sudo dnf install tkinter
```

### Câmera não funciona:
```bash
# Verificar câmeras disponíveis
ls /dev/video*

# Testar câmera
sudo apt install cheese
cheese  # Teste visual

# Permissões de câmera
sudo usermod -a -G video $USER
# Reiniciar sessão após comando acima
```

### Erro de permissões:
```bash
# Dar permissão de execução
chmod +x DETFACE

# Verificar propriedade dos arquivos
ls -la faces/ logs/ reports/
```

### Interface não aparece:
```bash
# Verificar display
echo $DISPLAY

# Para SSH com X11:
ssh -X usuario@server
```

## ESTRUTURA DE PASTAS

- faces/: Fotos dos usuários cadastrados
- logs/: Registros do sistema
- reports/: Relatórios gerados
- backup/: Backups automáticos  
- config.json: Configurações do sistema
- users.json: Dados dos usuários

## BACKUP E SEGURANÇA

```bash
# Backup completo
tar -czf detface_backup_$(date +%Y%m%d).tar.gz faces/ logs/ reports/ config.json users.json

# Restaurar backup
tar -xzf detface_backup_YYYYMMDD.tar.gz
```

## SUPORTE

Em caso de problemas:
1. Verifique logs: `cat logs/detface_$(date +%Y-%m-%d).log`
2. Verifique dependências: `ldd DETFACE`
3. Execute em modo debug: `./DETFACE --debug`
"""
    else:
        readme_content = """# DETFACE - Sistema de Reconhecimento Facial

Sistema básico de reconhecimento facial com interface gráfica.

Para mais informações, consulte a documentação do projeto.
"""
    
    with open(os.path.join(dist_folder, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

def create_linux_installer(dist_folder, executable_name):
    """Cria script de instalação para Linux"""
    installer_content = """#!/bin/bash
# Instalador do DETFACE para Linux

set -e

APP_NAME="DETFACE"
INSTALL_DIR="/opt/detface"
BIN_DIR="/usr/local/bin"
DESKTOP_FILE="/usr/share/applications/detface.desktop"

echo "🚀 Instalador do DETFACE"
echo "========================"

# Verificar se é root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Execute como root: sudo ./install.sh"
    exit 1
fi

echo "📦 Instalando DETFACE..."

# Criar diretório de instalação
mkdir -p "$INSTALL_DIR"

# Copiar arquivos
echo "📂 Copiando arquivos..."
cp -r . "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/DETFACE"

# Criar link simbólico
echo "🔗 Criando link do executável..."
ln -sf "$INSTALL_DIR/DETFACE" "$BIN_DIR/detface"

# Criar arquivo .desktop
echo "🖥️ Criando atalho do menu..."
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=DETFACE
Comment=Sistema de Reconhecimento Facial
Exec=$INSTALL_DIR/DETFACE
Icon=camera
Terminal=false
Type=Application
Categories=Office;Photography;Security;
StartupNotify=true
EOF

# Instalar dependências se possível
echo "📋 Verificando dependências..."
if command -v apt &> /dev/null; then
    apt update
    apt install -y python3-tk libopencv-dev libgl1-mesa-glx libglib2.0-0
elif command -v dnf &> /dev/null; then
    dnf install -y tkinter opencv-devel mesa-libGL glib2
elif command -v pacman &> /dev/null; then
    pacman -S --noconfirm tk opencv mesa glib2
else
    echo "⚠️ Instale manualmente: tkinter, opencv, mesa, glib2"
fi

echo "✅ Instalação concluída!"
echo ""
echo "Como usar:"
echo "- Terminal: detface"
echo "- Menu: Procure por 'DETFACE'"
echo "- Diretório: $INSTALL_DIR"
echo ""
echo "Para desinstalar:"
echo "sudo rm -rf $INSTALL_DIR"  
echo "sudo rm $BIN_DIR/detface"
echo "sudo rm $DESKTOP_FILE"
"""
    
    installer_path = os.path.join(dist_folder, 'install.sh')
    with open(installer_path, 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    # Tornar executável
    os.chmod(installer_path, 0o755)
    
    print("🐧 Script de instalação Linux criado: install.sh")

def main():
    system_name, ext = get_system_info()
    
    print("🚀 DETFACE - Gerador de Executável Multiplataforma")
    print("=" * 60)
    print(f"🖥️ Sistema detectado: {system_name.upper()}")
    print(f"📁 Executável será: DETFACE{ext}")
    print()
    
    # Verificar se arquivos necessários existem
    required_files = ['detface_desktop.py', 'face_detector.py', 'user_manager.py', 'report_generator.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Arquivos necessários não encontrados: {missing_files}")
        return False
    
    # Criar pastas se não existirem
    print("📂 Preparando estrutura de pastas...")
    for folder in ['faces', 'logs', 'reports', 'backup', 'templates']:
        if not os.path.exists(folder):
            os.makedirs(folder)
            with open(os.path.join(folder, '.gitkeep'), 'w') as f:
                f.write('')
    
    # Verificar se arquivos de configuração existem
    config_files = ['config.json', 'users.json']
    for config_file in config_files:
        if not os.path.exists(config_file):
            print(f"⚠️ Criando {config_file} padrão...")
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
                import json
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
            elif config_file == 'users.json':
                with open(config_file, 'w') as f:
                    f.write('{}')
    
    # Compilar executável
    print("🔨 Iniciando processo de compilação...")
    success, dist_folder = build_executable()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 EXECUTÁVEL CRIADO COM SUCESSO!")
        print("=" * 60)
        print(f"📦 Pacote: {dist_folder}/")
        print(f"🚀 Executável: {dist_folder}/DETFACE{ext}")
        print(f"📖 Manual: {dist_folder}/README.txt")
        
        if system_name == 'linux':
            print(f"🐧 Instalador: {dist_folder}/install.sh")
            print("\n📋 Próximos passos para Linux:")
            print(f"   cd {dist_folder}")
            print("   chmod +x DETFACE")
            print("   ./DETFACE")
            print("\n   Ou para instalar no sistema:")
            print("   sudo ./install.sh")
            
        elif system_name == 'windows':
            print("\n📋 Próximos passos para Windows:")
            print(f"   1. Copie a pasta {dist_folder} para onde desejar")
            print("   2. Execute DETFACE.exe")
            print("   3. Veja o README.txt para solução de problemas")
        
        print(f"\n📊 Informações do executável:")
        if dist_folder:
            exe_path = os.path.join(dist_folder, f'DETFACE{ext}')
            if os.path.exists(exe_path):
                file_size = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"   Tamanho: {file_size:.1f} MB")
        
        print("\n✅ Pronto para distribuir!")
        
    else:
        print("\n" + "=" * 60)
        print("❌ ERRO NA COMPILAÇÃO")
        print("=" * 60)
        print("🔍 Verifique:")
        print("   - Todas as dependências estão instaladas")
        print("   - PyInstaller está funcionando")
        print("   - Não há erros nos arquivos Python")
        print("   - Há espaço suficiente em disco")
    
    return success

if __name__ == "__main__":
    main()