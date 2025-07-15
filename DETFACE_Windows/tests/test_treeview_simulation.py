#!/usr/bin/env python3
"""
Script para simular o comportamento do TreeView e identificar problemas
"""

import tkinter as tk
from tkinter import ttk
from user_manager import UserManager

def simulate_treeview():
    """Simula o comportamento do TreeView"""
    
    print("🧪 SIMULAÇÃO DO TREEVIEW")
    print("=" * 50)
    
    # Criar janela Tkinter
    root = tk.Tk()
    root.withdraw()  # Esconder janela
    
    # Criar TreeView
    tree = ttk.Treeview(root, columns=("id", "name", "dept", "position", "date", "records"), show="headings")
    
    # Configurar colunas
    tree.heading("id", text="ID")
    tree.heading("name", text="Nome")
    tree.heading("dept", text="Departamento")
    tree.heading("position", text="Cargo")
    tree.heading("date", text="Data Cadastro")
    tree.heading("records", text="Registros")
    
    # Carregar dados
    user_manager = UserManager()
    users = user_manager.get_all_users()
    
    print("Inserindo usuários no TreeView:")
    for user in users:
        dept = user.get('department', '-')
        position = user.get('position', '-')
        
        values = (
            user['id'], 
            user['name'], 
            dept,
            position,
            user['registered_date'], 
            0  # record_count
        )
        
        tree.insert("", tk.END, values=values)
        print(f"  Inserido: {values}")
    
    # Simular seleção
    print("\nSimulando seleção de usuários:")
    for item in tree.get_children():
        tree.selection_set(item)
        selected_item = tree.selection()[0]
        item_data = tree.item(selected_item)
        
        print(f"  Item selecionado: {item_data['values']}")
        user_id = item_data['values'][0]
        user_name = item_data['values'][1]
        
        print(f"    ID extraído: '{user_id}' (tipo: {type(user_id)})")
        print(f"    Nome extraído: '{user_name}' (tipo: {type(user_name)})")
        
        # Testar busca no UserManager
        user_data = user_manager.get_user(user_id)
        print(f"    get_user({user_id}): {'✅' if user_data else '❌'}")
        
        # Testar com conversão de string
        user_id_str = str(user_id)
        user_data_str = user_manager.get_user(user_id_str)
        print(f"    get_user('{user_id_str}'): {'✅' if user_data_str else '❌'}")
        
        print()
    
    root.destroy()

if __name__ == "__main__":
    simulate_treeview() 