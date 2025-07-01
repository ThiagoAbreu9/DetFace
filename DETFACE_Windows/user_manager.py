#!/usr/bin/env python3
"""
DETFACE - Gerenciador de Usuários
Responsável pelo cadastro, remoção e gerenciamento de usuários do sistema
"""

import json
import os
import datetime
from pathlib import Path
import shutil

class UserManager:
    """Classe responsável pelo gerenciamento de usuários"""
    
    def __init__(self):
        """Inicializa o gerenciador de usuários"""
        self.users_file = "users.json"
        self.faces_dir = Path("faces")
        self.users_data = self.load_users()
        
    def load_users(self):
        """Carrega dados dos usuários do arquivo JSON"""
        if not os.path.exists(self.users_file):
            return {}
            
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
            
    def save_users(self):
        """Salva dados dos usuários no arquivo JSON"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar usuários: {str(e)}")
            return False
            
    def add_user(self, name, user_id, additional_info=None):
        """Adiciona um novo usuário ao sistema"""
        # Verificar se usuário já existe
        if user_id in self.users_data:
            print(f"⚠️ Usuário com ID '{user_id}' já existe!")
            return False
            
        # Criar dados do usuário
        user_data = {
            'id': user_id,
            'name': name,
            'registered_date': datetime.datetime.now().isoformat(),
            'active': True,
            'last_seen': None,
            'total_entries': 0,
            'total_exits': 0
        }
        
        # Adicionar informações adicionais se fornecidas
        if additional_info:
            user_data.update(additional_info)
            
        # Salvar no dicionário
        self.users_data[user_id] = user_data
        
        # Salvar no arquivo
        if self.save_users():
            print(f"✅ Usuário '{name}' adicionado com sucesso!")
            return True
        else:
            # Reverter se falhou ao salvar
            del self.users_data[user_id]
            return False
            
    def remove_user(self, user_id):
        """Remove um usuário do sistema"""
        if user_id not in self.users_data:
            print(f"❌ Usuário com ID '{user_id}' não encontrado!")
            return False
            
        try:
            # Backup dos dados antes de remover
            user_data = self.users_data[user_id].copy()
            
            # Remover do dicionário
            del self.users_data[user_id]
            
            # Remover arquivo de imagem se existir
            image_files = [
                self.faces_dir / f"{user_id}.jpg",
                self.faces_dir / f"{user_id}.jpeg",
                self.faces_dir / f"{user_id}.png",
                self.faces_dir / f"{user_id}.bmp"
            ]
            
            for image_file in image_files:
                if image_file.exists():
                    image_file.unlink()
                    print(f"🗑️ Imagem removida: {image_file}")
                    
            # Salvar alterações
            if self.save_users():
                print(f"✅ Usuário '{user_data['name']}' removido com sucesso!")
                return True
            else:
                # Reverter se falhou ao salvar
                self.users_data[user_id] = user_data
                return False
                
        except Exception as e:
            print(f"❌ Erro ao remover usuário: {str(e)}")
            return False
            
    def update_user(self, user_id, **kwargs):
        """Atualiza informações de um usuário"""
        if user_id not in self.users_data:
            print(f"❌ Usuário com ID '{user_id}' não encontrado!")
            return False
            
        # Atualizar campos fornecidos
        for key, value in kwargs.items():
            if key in self.users_data[user_id]:
                self.users_data[user_id][key] = value
                
        # Atualizar timestamp de modificação
        self.users_data[user_id]['modified_date'] = datetime.datetime.now().isoformat()
        
        return self.save_users()
        
    def get_user(self, user_id):
        """Retorna dados de um usuário específico"""
        return self.users_data.get(user_id)
        
    def get_all_users(self):
        """Retorna lista de todos os usuários"""
        users_list = []
        for user_id, user_data in self.users_data.items():
            users_list.append(user_data)
        return users_list
        
    def get_active_users(self):
        """Retorna apenas usuários ativos"""
        return [user for user in self.get_all_users() if user.get('active', True)]
        
    def deactivate_user(self, user_id):
        """Desativa um usuário sem removê-lo"""
        if user_id not in self.users_data:
            return False
            
        self.users_data[user_id]['active'] = False
        self.users_data[user_id]['deactivated_date'] = datetime.datetime.now().isoformat()
        return self.save_users()
        
    def activate_user(self, user_id):
        """Reativa um usuário"""
        if user_id not in self.users_data:
            return False
            
        self.users_data[user_id]['active'] = True
        if 'deactivated_date' in self.users_data[user_id]:
            del self.users_data[user_id]['deactivated_date']
        return self.save_users()
        
    def update_user_statistics(self, user_id, entry_type):
        """Atualiza estatísticas do usuário após registro de presença"""
        if user_id not in self.users_data:
            return False
            
        # Atualizar última vez visto
        self.users_data[user_id]['last_seen'] = datetime.datetime.now().isoformat()
        
        # Atualizar contadores
        if entry_type == "ENTRADA":
            self.users_data[user_id]['total_entries'] = self.users_data[user_id].get('total_entries', 0) + 1
        elif entry_type == "SAÍDA":
            self.users_data[user_id]['total_exits'] = self.users_data[user_id].get('total_exits', 0) + 1
            
        return self.save_users()
        
    def validate_user_data(self, name, user_id):
        """Valida dados do usuário antes do cadastro"""
        errors = []
        
        # Validar nome
        if not name or len(name.strip()) < 2:
            errors.append("Nome deve ter pelo menos 2 caracteres")
            
        if len(name) > 50:
            errors.append("Nome deve ter no máximo 50 caracteres")
            
        # Validar ID
        if not user_id or len(user_id.strip()) < 2:
            errors.append("ID deve ter pelo menos 2 caracteres")
            
        if len(user_id) > 20:
            errors.append("ID deve ter no máximo 20 caracteres")
            
        # Verificar caracteres válidos no ID
        if not user_id.replace('_', '').replace('-', '').isalnum():
            errors.append("ID deve conter apenas letras, números, _ e -")
            
        # Verificar se ID já existe
        if user_id in self.users_data:
            errors.append(f"ID '{user_id}' já está em uso")
            
        return errors
        
    def search_users(self, query):
        """Busca usuários por nome ou ID"""
        query = query.lower().strip()
        results = []
        
        for user_data in self.users_data.values():
            if (query in user_data['name'].lower() or 
                query in user_data['id'].lower()):
                results.append(user_data)
                
        return results
        
    def export_users(self, filepath=None):
        """Exporta dados dos usuários para arquivo"""
        if not filepath:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"backup/users_export_{timestamp}.json"
            
        try:
            Path(filepath).parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.users_data, f, indent=4, ensure_ascii=False)
                
            print(f"✅ Usuários exportados para: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao exportar usuários: {str(e)}")
            return False
            
    def import_users(self, filepath):
        """Importa dados de usuários de arquivo"""
        if not os.path.exists(filepath):
            print(f"❌ Arquivo não encontrado: {filepath}")
            return False
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
                
            # Validar estrutura dos dados
            for user_id, user_data in imported_data.items():
                if not isinstance(user_data, dict) or 'name' not in user_data:
                    print(f"❌ Dados inválidos para usuário: {user_id}")
                    return False
                    
            # Fazer backup dos dados atuais
            backup_file = f"backup/users_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.export_users(backup_file)
            
            # Importar dados
            conflicts = []
            imported_count = 0
            
            for user_id, user_data in imported_data.items():
                if user_id in self.users_data:
                    conflicts.append(user_id)
                else:
                    self.users_data[user_id] = user_data
                    imported_count += 1
                    
            # Salvar dados
            if self.save_users():
                print(f"✅ {imported_count} usuários importados com sucesso!")
                if conflicts:
                    print(f"⚠️ {len(conflicts)} usuários ignorados (IDs já existem): {', '.join(conflicts)}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Erro ao importar usuários: {str(e)}")
            return False
            
    def get_user_statistics(self):
        """Retorna estatísticas gerais dos usuários"""
        total_users = len(self.users_data)
        active_users = len(self.get_active_users())
        inactive_users = total_users - active_users
        
        # Usuário mais antigo
        oldest_user = None
        oldest_date = None
        
        for user_data in self.users_data.values():
            reg_date = datetime.datetime.fromisoformat(user_data['registered_date'])
            if oldest_date is None or reg_date < oldest_date:
                oldest_date = reg_date
                oldest_user = user_data['name']
                
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'oldest_user': oldest_user,
            'oldest_registration_date': oldest_date.strftime('%Y-%m-%d') if oldest_date else None
        }
        
        return stats
        
    def cleanup_orphaned_images(self):
        """Remove imagens de faces sem usuário correspondente"""
        if not self.faces_dir.exists():
            return
            
        removed_count = 0
        
        for image_file in self.faces_dir.iterdir():
            if image_file.is_file():
                # Extrair ID do nome do arquivo
                user_id = image_file.stem
                
                # Verificar se usuário existe
                if user_id not in self.users_data:
                    try:
                        image_file.unlink()
                        print(f"🗑️ Imagem órfã removida: {image_file.name}")
                        removed_count += 1
                    except Exception as e:
                        print(f"❌ Erro ao remover {image_file.name}: {str(e)}")
                        
        if removed_count > 0:
            print(f"✅ {removed_count} imagem(ns) órfã(s) removida(s)")
        else:
            print("✅ Nenhuma imagem órfã encontrada")
