#!/usr/bin/env python3
"""
Script para executar a aplicação desktop DETFACE
"""

import sys
import os

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from detface_desktop import DetfaceDesktopApp
    import tkinter as tk
    
    print("Iniciando DETFACE Desktop...")
    
    # Verificar se tkinter está disponível
    root = tk.Tk()
    root.withdraw()  # Esconder janela temporária
    
    # Configurar para ambiente VNC se necessário
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
    
    # Criar e executar aplicação
    root.deiconify()  # Mostrar janela
    app = DetfaceDesktopApp(root)
    root.mainloop()
    
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de que todas as dependências estão instaladas")
    sys.exit(1)
    
except Exception as e:
    print(f"Erro ao executar aplicação: {e}")
    sys.exit(1)