#!/usr/bin/env python3
"""
Script para testar problemas com tipos de dados do user_id
"""

import json
from user_manager import UserManager

def test_user_id_types():
    """Testa diferentes tipos de user_id"""
    
    print("🧪 TESTE DE TIPOS DE USER_ID")
    print("=" * 50)
    
    # Carregar dados do arquivo JSON
    try:
        with open("users.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Dados do arquivo users.json:")
        for user_id, user_data in data.items():
            print(f"  ID: '{user_id}' (tipo: {type(user_id)})")
            print(f"    Nome: {user_data.get('name', 'N/A')}")
            print(f"    ID interno: {user_data.get('id', 'N/A')} (tipo: {type(user_data.get('id', 'N/A'))})")
            print()
            
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return
    
    # Testar UserManager
    user_manager = UserManager()
    
    print("Testando UserManager:")
    users = user_manager.get_all_users()
    
    for user in users:
        user_id = user['id']
        print(f"  Usuário: {user['name']}")
        print(f"    ID: '{user_id}' (tipo: {type(user_id)})")
        
        # Testar get_user com string
        user_str = str(user_id)
        result_str = user_manager.get_user(user_str)
        print(f"    get_user('{user_str}'): {'✅' if result_str else '❌'}")
        
        # Testar get_user com int (se for numérico)
        try:
            user_int = int(user_id)
            result_int = user_manager.get_user(user_int)
            print(f"    get_user({user_int}): {'✅' if result_int else '❌'}")
        except ValueError:
            print(f"    get_user(int): N/A (não é numérico)")
        
        print()

if __name__ == "__main__":
    test_user_id_types() 