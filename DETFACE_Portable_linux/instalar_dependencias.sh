#!/bin/bash
# DETFACE - Instalador de Dependências Linux

echo "=========================================="
echo "  DETFACE - Instalador de Dependências"
echo "=========================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

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
