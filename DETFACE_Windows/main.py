#!/usr/bin/env python3
"""
DETFACE - Sistema de Reconhecimento Facial para Controle de Presença
Autor: Sistema DETFACE
Data: 2025-06-30
Versão: 1.0

Script principal do sistema de reconhecimento facial para controle de entrada e saída.
"""

import os
import sys
import time
import json
import datetime
from pathlib import Path

# Importar módulos do sistema
from face_detector import FaceDetector
from report_generator import ReportGenerator
from user_manager import UserManager

class DetfaceSystem:
    """Classe principal do sistema DETFACE"""
    
    def __init__(self):
        """Inicializa o sistema DETFACE"""
        self.setup_directories()
        self.load_config()
        self.face_detector = FaceDetector()
        self.report_generator = ReportGenerator()
        self.user_manager = UserManager()
        self.running = False
        
    def setup_directories(self):
        """Cria as pastas necessárias se não existirem"""
        directories = ['faces', 'logs', 'reports', 'backup']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            
    def load_config(self):
        """Carrega configurações do sistema"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Criar configuração padrão
            self.config = {
                "max_users": 10,
                "recognition_threshold": 0.6,
                "camera_index": 0,
                "auto_backup": True,
                "backup_interval_hours": 24,
                "log_level": "INFO"
            }
            self.save_config()
            
    def save_config(self):
        """Salva configurações no arquivo"""
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
            
    def log_event(self, message, level="INFO"):
        """Registra eventos no log do sistema"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Escrever no arquivo de log
        log_file = f"logs/detface_{datetime.date.today().strftime('%Y-%m-%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
        # Exibir no console se for erro ou warning
        if level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")
            
    def display_menu(self):
        """Exibe o menu principal do sistema"""
        print("\n" + "="*60)
        print("           DETFACE - Sistema de Reconhecimento Facial")
        print("              Controle de Presença e Permanência")
        print("="*60)
        print("\n🎯 OPÇÕES DISPONÍVEIS:")
        print("1. 📹 Iniciar Reconhecimento Facial")
        print("2. 👤 Cadastrar Novo Usuário")
        print("3. 📋 Listar Usuários Cadastrados")
        print("4. 📊 Gerar Relatório Semanal")
        print("5. 📈 Gerar Relatório Mensal")
        print("6. 🗑️  Remover Usuário")
        print("7. ⚙️  Configurações do Sistema")
        print("8. 📁 Backup dos Dados")
        print("9. 📋 Ver Logs do Sistema")
        print("0. ❌ Sair do Sistema")
        print("-"*60)
        
    def start_recognition(self):
        """Inicia o processo de reconhecimento facial"""
        if self.config.get("demo_mode", False):
            self.demo_recognition()
        else:
            print("\n🚀 Iniciando sistema de reconhecimento facial...")
            print("💡 Pressione 'q' para parar o reconhecimento")
            print("💡 Pressione 'SPACE' para capturar manualmente")
            
            try:
                self.face_detector.start_recognition()
                self.log_event("Sistema de reconhecimento iniciado")
            except Exception as e:
                error_msg = f"Erro ao iniciar reconhecimento: {str(e)}"
                self.log_event(error_msg, "ERROR")
                print(f"❌ {error_msg}")
    
    def demo_recognition(self):
        """Simula o reconhecimento facial em modo demo"""
        print("\n🎮 MODO DEMO - Simulação de Reconhecimento Facial")
        print("-"*50)
        print("Este é um modo de demonstração que simula o reconhecimento facial.")
        print("Em um ambiente real com câmera, o sistema detectaria e reconheceria rostos automaticamente.")
        
        # Simular alguns reconhecimentos
        users = self.user_manager.get_all_users()
        if users:
            print(f"\n📊 Usuários cadastrados: {len(users)}")
            for i, user in enumerate(users[:3]):  # Mostrar apenas os primeiros 3
                print(f"  {i+1}. {user['name']} (ID: {user['id']})")
            
            print("\n🎯 Simulando reconhecimentos...")
            import random
            for i in range(3):
                user = random.choice(users)
                # Simular registro de presença
                self.face_detector.register_attendance(user['id'], user['name'])
                time.sleep(1)  # Pausa para visualizar
                
            print("\n✅ Simulação concluída!")
        else:
            print("\n❌ Nenhum usuário cadastrado para simular reconhecimento.")
            print("Cadastre alguns usuários primeiro usando a opção 2 do menu.")
            
    def register_new_user(self):
        """Registra um novo usuário no sistema"""
        print("\n👤 CADASTRO DE NOVO USUÁRIO")
        print("-"*40)
        
        # Verificar limite de usuários
        current_users = len(self.user_manager.get_all_users())
        if current_users >= self.config["max_users"]:
            print(f"❌ Limite máximo de {self.config['max_users']} usuários atingido!")
            return
            
        # Solicitar dados do usuário
        name = input("📝 Nome completo do usuário: ").strip()
        if not name:
            print("❌ Nome é obrigatório!")
            return
            
        user_id = input("🆔 ID do usuário (opcional): ").strip()
        if not user_id:
            user_id = name.lower().replace(" ", "_")
            
        if self.config.get("demo_mode", False):
            # Modo demo - não precisa capturar foto
            print(f"\n🎮 MODO DEMO: Cadastrando usuário sem captura de foto...")
            try:
                self.user_manager.add_user(name, user_id)
                print(f"✅ Usuário '{name}' cadastrado com sucesso no modo demo!")
                self.log_event(f"Novo usuário cadastrado (modo demo): {name} (ID: {user_id})")
            except Exception as e:
                error_msg = f"Erro no cadastro: {str(e)}"
                self.log_event(error_msg, "ERROR")
                print(f"❌ {error_msg}")
        else:
            # Modo normal - capturar foto
            print(f"\n📸 Posicione-se na frente da câmera...")
            print("💡 Pressione SPACE para capturar ou 'q' para cancelar")
            
            try:
                success = self.face_detector.capture_user_face(name, user_id)
                if success:
                    self.user_manager.add_user(name, user_id)
                    print(f"✅ Usuário '{name}' cadastrado com sucesso!")
                    self.log_event(f"Novo usuário cadastrado: {name} (ID: {user_id})")
                else:
                    print("❌ Falha ao capturar imagem do usuário")
            except Exception as e:
                error_msg = f"Erro no cadastro: {str(e)}"
                self.log_event(error_msg, "ERROR")
                print(f"❌ {error_msg}")
            
    def list_users(self):
        """Lista todos os usuários cadastrados"""
        print("\n📋 USUÁRIOS CADASTRADOS")
        print("-"*50)
        
        users = self.user_manager.get_all_users()
        if not users:
            print("❌ Nenhum usuário cadastrado no sistema")
            return
            
        print(f"{'ID':<15} {'Nome':<25} {'Cadastrado em':<20}")
        print("-"*60)
        
        for user in users:
            print(f"{user['id']:<15} {user['name']:<25} {user['registered_date']:<20}")
            
        print(f"\n📊 Total: {len(users)} usuário(s) cadastrado(s)")
        
    def generate_weekly_report(self):
        """Gera relatório semanal"""
        print("\n📊 GERAÇÃO DE RELATÓRIO SEMANAL")
        print("-"*40)
        
        try:
            csv_file, pdf_file = self.report_generator.generate_weekly_report()
            print(f"✅ Relatório CSV gerado: {csv_file}")
            print(f"✅ Relatório PDF gerado: {pdf_file}")
            self.log_event("Relatório semanal gerado com sucesso")
        except Exception as e:
            error_msg = f"Erro ao gerar relatório semanal: {str(e)}"
            self.log_event(error_msg, "ERROR")
            print(f"❌ {error_msg}")
            
    def generate_monthly_report(self):
        """Gera relatório mensal"""
        print("\n📈 GERAÇÃO DE RELATÓRIO MENSAL")
        print("-"*40)
        
        try:
            csv_file, pdf_file = self.report_generator.generate_monthly_report()
            print(f"✅ Relatório CSV gerado: {csv_file}")
            print(f"✅ Relatório PDF gerado: {pdf_file}")
            self.log_event("Relatório mensal gerado com sucesso")
        except Exception as e:
            error_msg = f"Erro ao gerar relatório mensal: {str(e)}"
            self.log_event(error_msg, "ERROR")
            print(f"❌ {error_msg}")
            
    def remove_user(self):
        """Remove um usuário do sistema"""
        print("\n🗑️ REMOÇÃO DE USUÁRIO")
        print("-"*30)
        
        users = self.user_manager.get_all_users()
        if not users:
            print("❌ Nenhum usuário cadastrado no sistema")
            return
            
        # Listar usuários
        print("Usuários disponíveis:")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user['name']} (ID: {user['id']})")
            
        try:
            choice = int(input("\nEscolha o número do usuário para remover: "))
            if 1 <= choice <= len(users):
                user = users[choice - 1]
                confirm = input(f"Confirma remoção de '{user['name']}'? (s/N): ").lower()
                
                if confirm == 's':
                    self.user_manager.remove_user(user['id'])
                    print(f"✅ Usuário '{user['name']}' removido com sucesso!")
                    self.log_event(f"Usuário removido: {user['name']} (ID: {user['id']})")
                else:
                    print("❌ Remoção cancelada")
            else:
                print("❌ Opção inválida")
        except ValueError:
            print("❌ Entrada inválida")
            
    def show_settings(self):
        """Exibe e permite alterar configurações"""
        print("\n⚙️ CONFIGURAÇÕES DO SISTEMA")
        print("-"*40)
        
        print(f"Máximo de usuários: {self.config['max_users']}")
        print(f"Threshold de reconhecimento: {self.config['recognition_threshold']}")
        print(f"Índice da câmera: {self.config['camera_index']}")
        print(f"Backup automático: {'Sim' if self.config['auto_backup'] else 'Não'}")
        print(f"Intervalo de backup (horas): {self.config['backup_interval_hours']}")
        print(f"Nível de log: {self.config['log_level']}")
        
        change = input("\nDeseja alterar alguma configuração? (s/N): ").lower()
        if change == 's':
            self.modify_settings()
            
    def modify_settings(self):
        """Permite modificar configurações"""
        print("\n🔧 MODIFICAR CONFIGURAÇÕES")
        print("(Pressione ENTER para manter o valor atual)")
        
        # Máximo de usuários
        max_users = input(f"Máximo de usuários ({self.config['max_users']}): ").strip()
        if max_users.isdigit():
            self.config['max_users'] = int(max_users)
            
        # Threshold
        threshold = input(f"Threshold de reconhecimento ({self.config['recognition_threshold']}): ").strip()
        try:
            if threshold:
                threshold_val = float(threshold)
                if 0.0 <= threshold_val <= 1.0:
                    self.config['recognition_threshold'] = threshold_val
        except ValueError:
            pass
            
        # Índice da câmera
        camera_idx = input(f"Índice da câmera ({self.config['camera_index']}): ").strip()
        if camera_idx.isdigit():
            self.config['camera_index'] = int(camera_idx)
            
        self.save_config()
        print("✅ Configurações salvas com sucesso!")
        
    def backup_data(self):
        """Realiza backup dos dados"""
        print("\n📁 BACKUP DOS DADOS")
        print("-"*25)
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backup/backup_{timestamp}"
            Path(backup_dir).mkdir(exist_ok=True)
            
            # Copiar arquivos importantes
            import shutil
            
            # Backup do registro de presença
            if os.path.exists("registro_presenca.csv"):
                shutil.copy2("registro_presenca.csv", f"{backup_dir}/registro_presenca.csv")
                
            # Backup das configurações
            shutil.copy2("config.json", f"{backup_dir}/config.json")
            
            # Backup dos usuários
            if os.path.exists("users.json"):
                shutil.copy2("users.json", f"{backup_dir}/users.json")
                
            print(f"✅ Backup realizado em: {backup_dir}")
            self.log_event(f"Backup realizado: {backup_dir}")
            
        except Exception as e:
            error_msg = f"Erro no backup: {str(e)}"
            self.log_event(error_msg, "ERROR")
            print(f"❌ {error_msg}")
            
    def show_logs(self):
        """Exibe os logs do sistema"""
        print("\n📋 LOGS DO SISTEMA")
        print("-"*30)
        
        log_file = f"logs/detface_{datetime.date.today().strftime('%Y-%m-%d')}.log"
        
        if not os.path.exists(log_file):
            print("❌ Nenhum log encontrado para hoje")
            return
            
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()
                
            if not logs:
                print("📄 Log vazio")
                return
                
            # Mostrar últimas 20 linhas
            print("📄 Últimas 20 entradas do log:")
            print("-"*50)
            for line in logs[-20:]:
                print(line.strip())
                
        except Exception as e:
            print(f"❌ Erro ao ler logs: {str(e)}")
            
    def run(self):
        """Executa o loop principal do sistema"""
        print("🚀 Iniciando DETFACE...")
        self.log_event("Sistema DETFACE iniciado")
        
        # Verificar dependências
        if not self.face_detector.check_camera():
            print("⚠️ Câmera não detectada! Executando em modo DEMO.")
            print("🎮 No modo demo, você pode testar todas as funcionalidades exceto o reconhecimento em tempo real.")
            self.config["demo_mode"] = True
        else:
            self.config["demo_mode"] = False
            
        self.running = True
        
        while self.running:
            try:
                self.display_menu()
                choice = input("\n👉 Escolha uma opção: ").strip()
                
                if choice == "1":
                    self.start_recognition()
                elif choice == "2":
                    self.register_new_user()
                elif choice == "3":
                    self.list_users()
                elif choice == "4":
                    self.generate_weekly_report()
                elif choice == "5":
                    self.generate_monthly_report()
                elif choice == "6":
                    self.remove_user()
                elif choice == "7":
                    self.show_settings()
                elif choice == "8":
                    self.backup_data()
                elif choice == "9":
                    self.show_logs()
                elif choice == "0":
                    self.shutdown()
                else:
                    print("❌ Opção inválida! Tente novamente.")
                    
                # Pausar para o usuário ler a resposta
                if choice != "0":
                    input("\n⏸️ Pressione ENTER para continuar...")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupção detectada...")
                self.shutdown()
            except Exception as e:
                error_msg = f"Erro inesperado: {str(e)}"
                self.log_event(error_msg, "ERROR")
                print(f"❌ {error_msg}")
                
    def shutdown(self):
        """Encerra o sistema de forma segura"""
        print("\n🔄 Encerrando sistema...")
        
        # Realizar backup automático se configurado
        if self.config.get("auto_backup", True):
            try:
                self.backup_data()
            except:
                pass
                
        self.log_event("Sistema DETFACE encerrado")
        self.running = False
        print("✅ Sistema encerrado com sucesso!")
        print("👋 Obrigado por usar o DETFACE!")

def main():
    """Função principal do sistema"""
    try:
        system = DetfaceSystem()
        system.run()
    except Exception as e:
        print(f"❌ Erro crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
