# DETFACE - Sistema de Reconhecimento Facial

Sistema completo de reconhecimento facial para controle de presença e permanência, desenvolvido em Python com OpenCV.

## 🎯 Características Principais

- **Reconhecimento facial rápido** (menos de 3 segundos)
- **Suporte até 10 usuários** cadastrados
- **Registro automático** de entrada/saída com timestamps
- **Relatórios completos** em CSV e PDF
- **Interface desktop** com 4 abas organizadas
- **Funciona offline** após instalação
- **Portátil** - não precisa de servidor ou Docker

## 🖥️ Interface Desktop

O sistema possui uma interface gráfica intuitiva com 4 abas:

- **🎯 Reconhecimento**: Identifica pessoas em tempo real via câmera
- **👤 Cadastrar**: Registra novos usuários no sistema  
- **🔧 Administração**: Gerencia usuários cadastrados
- **📊 Relatórios**: Gera relatórios de presença (diário, semanal, mensal)

## 📁 Estrutura do Projeto

```
DETFACE/
├── detface_desktop.py      # Interface gráfica principal
├── face_detector.py        # Engine de reconhecimento facial
├── user_manager.py         # Gestão de usuários
├── report_generator.py     # Gerador de relatórios
├── web_camera.py          # Interface web (opcional)
├── main.py                # Sistema via terminal
├── config.json            # Configurações
├── users.json             # Base de dados de usuários
├── faces/                 # Fotos dos usuários cadastrados
├── logs/                  # Logs do sistema
├── reports/               # Relatórios gerados
└── backup/                # Backups automáticos
```

## 🚀 Instalação e Uso

### Windows

1. **Baixe**: `DETFACE_Windows.zip`
2. **Extraia** para uma pasta
3. **Instale Python**: https://python.org (marque "Add to PATH")
4. **Execute**: `instalar_dependencias.bat` (primeira vez)
5. **Use**: `DETFACE.bat`

### Linux

1. **Baixe**: `DETFACE_Portable_linux.zip`
2. **Extraia** para uma pasta
3. **Execute**: `./instalar_dependencias.sh` (primeira vez)
4. **Use**: `./DETFACE.sh`

## 📋 Requisitos do Sistema

- **Python 3.8+** (obrigatório)
- **4 GB RAM** mínimo
- **500 MB** espaço em disco
- **Câmera USB** (opcional - funciona sem câmera em modo demo)
- **Conexão internet** (só para instalar dependências)

### Dependências Python

```
opencv-python>=4.5.0
numpy>=1.21.0
pandas>=1.3.0
reportlab>=3.6.0
scikit-learn>=1.0.0
Pillow>=8.3.0
openpyxl>=3.0.0
```

## 🎮 Modo Demo

O sistema funciona mesmo sem câmera:
- Teste todas as funcionalidades
- Cadastre usuários manualmente
- Gere relatórios de demonstração
- Configure o sistema

## 🔒 Segurança e Privacidade

- ✅ **Dados locais**: Tudo fica no seu computador
- ✅ **Offline**: Funciona sem internet (após instalação)
- ✅ **Sem cloud**: Nenhum dado é enviado para servidores
- ✅ **Controle total**: Você gerencia todos os dados

## 📊 Funcionalidades

### Reconhecimento Facial
- Detecção em tempo real via câmera
- Algoritmo baseado em OpenCV
- Limiar de confiança configurável
- Cooldown para evitar registros duplicados

### Gestão de Usuários
- Cadastro com foto facial
- Edição de informações
- Remoção segura com confirmação
- Busca e filtros

### Relatórios
- **Diário**: Presenças do dia atual
- **Semanal**: Últimos 7 dias
- **Mensal**: Últimos 30 dias
- **Personalizado**: Período específico
- **Formatos**: CSV (dados) e PDF (apresentação)

## ⚙️ Configuração

O arquivo `config.json` permite ajustar:

```json
{
  "camera_index": 0,
  "recognition_threshold": 0.7,
  "recognition_cooldown": 5,
  "max_faces": 10,
  "auto_backup": true,
  "backup_interval": 7,
  "log_level": "INFO"
}
```

## 🔧 Solução de Problemas

### Python não encontrado
- Instale Python de python.org
- Marque "Add Python to PATH" na instalação
- Reinicie o computador

### Erro ao instalar dependências
- Execute como Administrador
- Verifique conexão com internet
- Desative antivírus temporariamente

### Câmera não funciona
- Sistema funciona sem câmera (modo demo)
- Teste a câmera no aplicativo padrão do SO
- Verifique drivers da câmera

## 🛠️ Desenvolvimento

### Tecnologias Utilizadas
- **Python**: Linguagem principal
- **OpenCV**: Processamento de imagem e reconhecimento
- **tkinter**: Interface gráfica nativa
- **pandas**: Manipulação de dados
- **ReportLab**: Geração de PDFs
- **JSON/CSV**: Armazenamento de dados

### Arquitetura
- **Modular**: Cada funcionalidade em arquivo separado
- **Orientada a objetos**: Classes especializadas
- **Configurável**: JSON para todas as configurações
- **Portátil**: Sem dependências externas complexas

## 📦 Releases

- **v1.0** - Sistema base com reconhecimento facial
- **v1.1** - Interface desktop com abas
- **v1.2** - Relatórios em PDF
- **v1.3** - Modo demo e melhor detecção de câmera

## 📄 Licença

Este projeto é distribuído sob licença open source. Veja o arquivo LICENSE para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! 

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para suporte técnico:
- Verifique a documentação completa nos arquivos README.txt
- Consulte os logs na pasta `logs/`
- Abra uma issue neste repositório

---

**DETFACE** - Sistema profissional de reconhecimento facial para controle de presença