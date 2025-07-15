#!/usr/bin/env python3
"""
Script de teste para verificar as funcionalidades de gerenciamento de usuários
"""

import json
import os
from user_manager import UserManager

def test_user_management():
    """Testa as funcionalidades de gerenciamento de usuários"""
    
    print("🧪 TESTE DE GERENCIAMENTO DE USUÁRIOS")
    print("=" * 50)
    
    # Inicializar UserManager
    user_manager = UserManager()
    
    # Teste 1: Verificar se consegue carregar usuários
    print("\n1. Testando carregamento de usuários...")
    users = user_manager.get_all_users()
    print(f"   Usuários carregados: {len(users)}")
    for user in users:
        print(f"   - {user['name']} (ID: {user['id']})")
    
    # Teste 2: Verificar se consegue obter usuário específico
    print("\n2. Testando obtenção de usuário específico...")
    if users:
        test_user = users[0]
        user_id = test_user['id']
        user_data = user_manager.get_user(user_id)
        if user_data:
            print(f"   ✅ Usuário encontrado: {user_data['name']}")
        else:
            print(f"   ❌ Usuário não encontrado: {user_id}")
    
    # Teste 3: Testar atualização de usuário
    print("\n3. Testando atualização de usuário...")
    if users:
        test_user = users[0]
        user_id = test_user['id']
        original_name = test_user['name']
        
        # Tentar atualizar
        success = user_manager.update_user(user_id, name="Nome Teste Atualizado")
        if success:
            print(f"   ✅ Usuário atualizado com sucesso")
            
            # Verificar se foi realmente atualizado
            updated_user = user_manager.get_user(user_id)
            if updated_user and updated_user['name'] == "Nome Teste Atualizado":
                print(f"   ✅ Verificação: nome atualizado para '{updated_user['name']}'")
            else:
                print(f"   ❌ Verificação falhou: nome não foi atualizado")
            
            # Reverter mudança
            user_manager.update_user(user_id, name=original_name)
            print(f"   🔄 Mudança revertida")
        else:
            print(f"   ❌ Falha ao atualizar usuário")
    
    # Teste 4: Verificar estrutura do arquivo JSON
    print("\n4. Verificando estrutura do arquivo users.json...")
    try:
        with open("users.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   Estrutura do arquivo:")
        for user_id, user_data in data.items():
            print(f"   - ID: {user_id}")
            print(f"     Nome: {user_data.get('name', 'N/A')}")
            print(f"     Departamento: {user_data.get('department', 'N/A')}")
            print(f"     Cargo: {user_data.get('position', 'N/A')}")
            print(f"     Data: {user_data.get('registered_date', 'N/A')}")
            print()
            
    except Exception as e:
        print(f"   ❌ Erro ao ler arquivo: {e}")
    
    # Teste 5: Verificar se as funções do UserManager estão funcionando
    print("\n5. Testando funções do UserManager...")
    
    # Testar get_user
    if users:
        test_user = users[0]
        user_id = test_user['id']
        user_data = user_manager.get_user(user_id)
        print(f"   get_user({user_id}): {'✅' if user_data else '❌'}")
    
    # Testar get_all_users
    all_users = user_manager.get_all_users()
    print(f"   get_all_users(): {'✅' if all_users else '❌'} ({len(all_users)} usuários)")
    
    # Testar get_active_users
    active_users = user_manager.get_active_users()
    print(f"   get_active_users(): {'✅' if active_users else '❌'} ({len(active_users)} usuários)")
    
    print("\n" + "=" * 50)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    test_user_management() 