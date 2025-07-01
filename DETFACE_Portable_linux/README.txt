# DETFACE - Sistema de Reconhecimento Facial
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
tar -czf detface_backup_$(date +%Y%m%d).tar.gz \
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
