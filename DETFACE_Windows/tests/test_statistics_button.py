#!/usr/bin/env python3
"""
Teste para verificar se o botão de atualizar estatísticas está funcionando
"""

import tkinter as tk
from tkinter import ttk
from user_manager import UserManager
import os
import csv
from datetime import datetime

def test_statistics_button():
    """Testa a funcionalidade do botão de estatísticas"""
    
    print("🧪 TESTE DO BOTÃO DE ESTATÍSTICAS")
    print("=" * 50)
    
    # Criar janela Tkinter
    root = tk.Tk()
    root.withdraw()  # Esconder janela
    
    # Criar frame de estatísticas (simulando a interface)
    stats_frame = ttk.LabelFrame(root, text="Estatísticas do Sistema", padding=15)
    stats_frame.pack(fill=tk.X, padx=20, pady=20)
    
    stats_container = ttk.Frame(stats_frame)
    stats_container.pack(fill=tk.X)
    
    # Criar variáveis (como na interface real)
    total_users_var = tk.StringVar(value="0")
    total_records_var = tk.StringVar(value="0")
    today_records_var = tk.StringVar(value="0")
    
    # Criar labels
    ttk.Label(stats_container, text="Total de Usuários:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
    ttk.Label(stats_container, textvariable=total_users_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W, padx=(0, 30))
    
    ttk.Label(stats_container, text="Total de Registros:", font=("Arial", 12)).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
    ttk.Label(stats_container, textvariable=total_records_var, font=("Arial", 12, "bold")).grid(row=0, column=3, sticky=tk.W, padx=(0, 30))
    
    ttk.Label(stats_container, text="Registros Hoje:", font=("Arial", 12)).grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
    ttk.Label(stats_container, textvariable=today_records_var, font=("Arial", 12, "bold")).grid(row=0, column=5, sticky=tk.W)
    
    # Função de atualização (simulando a função real)
    def update_statistics():
        """Atualiza estatísticas do sistema"""
        try:
            print("🔄 Atualizando estatísticas...")
            
            # Total de usuários
            user_manager = UserManager()
            users = user_manager.get_all_users()
            total_users = len(users)
            total_users_var.set(str(total_users))
            print(f"   Total de usuários: {total_users}")
            
            # Total de registros
            total_records = 0
            today_records = 0
            today = datetime.now().strftime('%Y-%m-%d')
            
            if os.path.exists("registro_presenca.csv"):
                with open("registro_presenca.csv", 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        total_records += 1
                        if row['timestamp'].startswith(today):
                            today_records += 1
            
            total_records_var.set(str(total_records))
            today_records_var.set(str(today_records))
            
            print(f"   Total de registros: {total_records}")
            print(f"   Registros hoje: {today_records}")
            print("   ✅ Estatísticas atualizadas com sucesso!")
            
        except Exception as e:
            print(f"   ❌ Erro ao atualizar estatísticas: {e}")
    
    # Criar botão
    update_button = ttk.Button(stats_frame, text="🔄 Atualizar Estatísticas", 
                              command=update_statistics)
    update_button.pack(pady=(10, 0))
    
    print("Interface criada. Testando botão...")
    
    # Simular clique no botão
    print("\nSimulando clique no botão 'Atualizar Estatísticas'...")
    update_statistics()
    
    # Verificar valores finais
    print(f"\nValores finais das variáveis:")
    print(f"   total_users_var: '{total_users_var.get()}'")
    print(f"   total_records_var: '{total_records_var.get()}'")
    print(f"   today_records_var: '{today_records_var.get()}'")
    
    root.destroy()
    
    print("\n" + "=" * 50)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    test_statistics_button() 