#!/bin/bash
# DETFACE - Sistema de Reconhecimento Facial

echo "========================================"
echo "     DETFACE - Sistema Iniciando..."  
echo "========================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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
