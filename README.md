# DETFACE - Sistema de Reconhecimento Facial

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

Sistema completo de reconhecimento facial para controle de presença e permanência, desenvolvido em Python com OpenCV e face_recognition.

## 🎯 Características Principais

- **Reconhecimento Facial Rápido**: Processamento em menos de 3 segundos
- **Controle de Acesso**: Até 10 usuários cadastrados
- **Registro Automático**: Entrada e saída com timestamp
- **Relatórios Completos**: Geração em CSV e PDF
- **Interface Simples**: Terminal interativo
- **Segurança**: Armazena apenas metadados, não imagens biométricas

## 🚀 Instalação

### Pré-requisitos

```bash
# Python 3.8 ou superior
python --version

# Bibliotecas necessárias (instalar via pip)
pip install opencv-python
pip install face-recognition
pip install pandas
pip install reportlab
pip install openpyxl
pip install numpy
