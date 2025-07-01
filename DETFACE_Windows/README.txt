# DETFACE - Sistema de Reconhecimento Facial
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
