#!/usr/bin/env python3
"""
Script final para testar se as correções das funcionalidades funcionaram
"""

import tkinter as tk
from tkinter import ttk, messagebox
from user_manager import UserManager

def test_fixed_functions():
    """Testa as funcionalidades corrigidas"""
    
    print("🧪 TESTE FINAL - FUNCIONALIDADES CORRIGIDAS")
    print("=" * 60)
    
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
    
    print("Usuários carregados:")
    for user in users:
        dept = user.get('department', '-')
        position = user.get('position', '-')
        
        values = (
            user['id'], 
            user['name'], 
            dept,
            position,
            user['registered_date'], 
            0
        )
        
        tree.insert("", tk.END, values=values)
        print(f"  - {user['name']} (ID: {user['id']})")
    
    # Testar simulação das funções corrigidas
    print("\nTestando simulação das funções:")
    
    for item in tree.get_children():
        tree.selection_set(item)
        selected_item = tree.selection()[0]
        item_data = tree.item(selected_item)
        
        user_id = str(item_data['values'][0])  # Converter para string (CORREÇÃO)
        user_name = item_data['values'][1]
        
        print(f"\n  Usuário: {user_name}")
        print(f"    ID original: {item_data['values'][0]} (tipo: {type(item_data['values'][0])})")
        print(f"    ID convertido: '{user_id}' (tipo: {type(user_id)})")
        
        # Testar get_user
        user_data = user_manager.get_user(user_id)
        print(f"    get_user('{user_id}'): {'✅' if user_data else '❌'}")
        
        if user_data:
            print(f"      Nome encontrado: {user_data['name']}")
            
            # Testar update_user
            original_name = user_data['name']
            test_name = f"{original_name} (TESTE)"
            
            success = user_manager.update_user(user_id, name=test_name)
            print(f"    update_user: {'✅' if success else '❌'}")
            
            if success:
                # Verificar se foi atualizado
                updated_user = user_manager.get_user(user_id)
                if updated_user and updated_user['name'] == test_name:
                    print(f"      ✅ Nome atualizado para: {updated_user['name']}")
                else:
                    print(f"      ❌ Falha na verificação da atualização")
                
                # Reverter mudança
                user_manager.update_user(user_id, name=original_name)
                print(f"      🔄 Mudança revertida")
            else:
                print(f"      ❌ Falha na atualização")
    
    root.destroy()
    
    print("\n" + "=" * 60)
    print("✅ Teste final concluído!")
    print("\nAgora você pode testar as funcionalidades na interface:")
    print("1. Ver detalhes - deve abrir a janela com informações do usuário")
    print("2. Editar - deve abrir a janela de edição e permitir salvar")
    print("3. Excluir - deve confirmar e excluir o usuário")

if __name__ == "__main__":
    test_fixed_functions() 