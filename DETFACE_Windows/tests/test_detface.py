#!/usr/bin/env python3
"""
DETFACE - Testes Automatizados
Testes pytest para todas as funcionalidades do sistema de reconhecimento facial
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import cv2

# Importar módulos do sistema
from face_detector import FaceDetector
from user_manager import UserManager
from report_generator import ReportGenerator
from main import DetfaceSystem

class TestDetfaceSystem:
    """Classe principal de testes para o sistema DETFACE"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Configura ambiente de teste com arquivos temporários"""
        # Criar diretório temporário para testes
        self.test_dir = tempfile.mkdtemp(prefix="detface_test_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Criar estrutura de diretórios
        for dir_name in ['faces', 'logs', 'reports', 'backup']:
            Path(dir_name).mkdir(exist_ok=True)
        
        # Criar arquivo de configuração de teste
        self.test_config = {
            "max_users": 5,
            "recognition_threshold": 0.6,
            "camera_index": 0,
            "auto_backup": True,
            "backup_interval_hours": 24,
            "log_level": "INFO",
            "system_name": "DETFACE_TEST",
            "version": "1.0.0",
            "language": "pt-BR",
            "timezone": "America/Sao_Paulo"
        }
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_config, f, indent=4)
        
        yield
        
        # Limpeza após testes
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_01_system_initialization(self):
        """Testa inicialização do sistema principal"""
        system = DetfaceSystem()
        assert system is not None
        assert hasattr(system, 'config')
        assert system.config['system_name'] == 'DETFACE_TEST'
        assert system.config['max_users'] == 5
    
    def test_02_user_manager_initialization(self):
        """Testa inicialização do gerenciador de usuários"""
        user_manager = UserManager()
        assert user_manager is not None
        assert hasattr(user_manager, 'users_data')
        assert isinstance(user_manager.users_data, dict)
    
    def test_03_face_detector_initialization(self):
        """Testa inicialização do detector facial"""
        face_detector = FaceDetector()
        assert face_detector is not None
        assert hasattr(face_detector, 'face_cascade')
        assert hasattr(face_detector, 'known_face_features')
    
    def test_04_report_generator_initialization(self):
        """Testa inicialização do gerador de relatórios"""
        report_generator = ReportGenerator()
        assert report_generator is not None
        assert hasattr(report_generator, 'reports_dir')
        assert report_generator.reports_dir.exists()
    
    def test_05_add_user_success(self):
        """Testa adição bem-sucedida de usuário"""
        user_manager = UserManager()
        
        # Adicionar usuário
        result = user_manager.add_user("João Silva", "joao_silva")
        assert result is True
        
        # Verificar se usuário foi adicionado
        user = user_manager.get_user("joao_silva")
        assert user is not None
        assert user['name'] == "João Silva"
        assert user['id'] == "joao_silva"
        assert user['active'] is True
        assert 'registered_date' in user
    
    def test_06_add_user_duplicate(self):
        """Testa tentativa de adicionar usuário duplicado"""
        user_manager = UserManager()
        
        # Adicionar primeiro usuário
        user_manager.add_user("João Silva", "joao_silva")
        
        # Tentar adicionar usuário com mesmo ID
        result = user_manager.add_user("João Silva 2", "joao_silva")
        assert result is False
    
    def test_07_remove_user_success(self):
        """Testa remoção bem-sucedida de usuário"""
        user_manager = UserManager()
        
        # Adicionar usuário
        user_manager.add_user("Maria Santos", "maria_santos")
        
        # Remover usuário
        result = user_manager.remove_user("maria_santos")
        assert result is True
        
        # Verificar se usuário foi removido
        user = user_manager.get_user("maria_santos")
        assert user is None
    
    def test_08_remove_user_not_found(self):
        """Testa tentativa de remover usuário inexistente"""
        user_manager = UserManager()
        
        result = user_manager.remove_user("usuario_inexistente")
        assert result is False
    
    def test_09_update_user(self):
        """Testa atualização de dados do usuário"""
        user_manager = UserManager()
        
        # Adicionar usuário
        user_manager.add_user("Pedro Costa", "pedro_costa")
        
        # Atualizar dados
        result = user_manager.update_user("pedro_costa", name="Pedro Costa Silva")
        assert result is True
        
        # Verificar atualização
        user = user_manager.get_user("pedro_costa")
        assert user['name'] == "Pedro Costa Silva"
        assert 'modified_date' in user
    
    def test_10_get_all_users(self):
        """Testa obtenção de todos os usuários"""
        user_manager = UserManager()
        
        # Adicionar múltiplos usuários
        user_manager.add_user("Ana Silva", "ana_silva")
        user_manager.add_user("Carlos Lima", "carlos_lima")
        user_manager.add_user("Lucia Santos", "lucia_santos")
        
        # Obter todos os usuários
        users = user_manager.get_all_users()
        assert len(users) == 3
        
        # Verificar se todos os usuários estão presentes
        user_names = [user['name'] for user in users]
        assert "Ana Silva" in user_names
        assert "Carlos Lima" in user_names
        assert "Lucia Santos" in user_names
    
    def test_11_get_active_users(self):
        """Testa obtenção apenas de usuários ativos"""
        user_manager = UserManager()
        
        # Adicionar usuários
        user_manager.add_user("Ativo 1", "ativo1")
        user_manager.add_user("Ativo 2", "ativo2")
        user_manager.add_user("Inativo", "inativo")
        
        # Desativar um usuário
        user_manager.deactivate_user("inativo")
        
        # Obter usuários ativos
        active_users = user_manager.get_active_users()
        assert len(active_users) == 2
        
        # Verificar se apenas usuários ativos estão presentes
        active_names = [user['name'] for user in active_users]
        assert "Ativo 1" in active_names
        assert "Ativo 2" in active_names
        assert "Inativo" not in active_names
    
    def test_12_validate_user_data(self):
        """Testa validação de dados do usuário"""
        user_manager = UserManager()
        
        # Teste com dados válidos
        errors = user_manager.validate_user_data("Nome Válido", "id_valido")
        assert len(errors) == 0
        
        # Teste com nome muito curto
        errors = user_manager.validate_user_data("A", "id_valido")
        assert len(errors) > 0
        assert "Nome deve ter pelo menos 2 caracteres" in errors
        
        # Teste com nome muito longo
        long_name = "A" * 51
        errors = user_manager.validate_user_data(long_name, "id_valido")
        assert len(errors) > 0
        assert "Nome deve ter no máximo 50 caracteres" in errors
        
        # Teste com ID muito curto
        errors = user_manager.validate_user_data("Nome Válido", "a")
        assert len(errors) > 0
        assert "ID deve ter pelo menos 2 caracteres" in errors
    
    def test_13_search_users(self):
        """Testa busca de usuários"""
        user_manager = UserManager()
        
        # Adicionar usuários
        user_manager.add_user("João Silva", "joao_silva")
        user_manager.add_user("Maria Silva", "maria_silva")
        user_manager.add_user("Carlos Santos", "carlos_santos")
        
        # Buscar por "Silva"
        results = user_manager.search_users("Silva")
        assert len(results) == 2
        
        # Buscar por "Carlos"
        results = user_manager.search_users("Carlos")
        assert len(results) == 1
        assert results[0]['name'] == "Carlos Santos"
    
    def test_14_face_detection_initialization(self):
        """Testa inicialização do detector facial"""
        face_detector = FaceDetector()
        
        # Verificar se o cascade classifier foi carregado
        assert face_detector.face_cascade is not None
        
        # Verificar configurações padrão
        assert face_detector.recognition_threshold == 0.75
        assert face_detector.recognition_cooldown == 5
    
    def test_15_face_feature_extraction(self):
        """Testa extração de características faciais"""
        face_detector = FaceDetector()
        
        # Criar imagem de teste (face simulada)
        test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        # Extrair características
        features = face_detector.extract_face_features(test_image)
        
        # Verificar se características foram extraídas
        assert features is not None
        assert len(features) == 256  # Histograma de 256 bins
        assert np.sum(features) > 0  # Não deve ser zero
    
    def test_16_camera_check(self):
        """Testa verificação de câmera (pode falhar se não houver câmera)"""
        face_detector = FaceDetector()
        
        # Tentar verificar câmera
        camera_available = face_detector.check_camera()
        
        # O teste deve passar independentemente de ter câmera ou não
        assert isinstance(camera_available, bool)
    
    def test_17_report_generation_csv(self):
        """Testa geração de relatório CSV"""
        report_generator = ReportGenerator()
        
        # Criar dados de teste
        test_data = pd.DataFrame({
            'Data': ['2025-01-01', '2025-01-01', '2025-01-02'],
            'Hora': ['08:00:00', '17:00:00', '08:30:00'],
            'Nome': ['João', 'João', 'Maria'],
            'ID_Usuario': ['joao', 'joao', 'maria'],
            'Tipo': ['ENTRADA', 'SAÍDA', 'ENTRADA'],
            'Timestamp': [
                datetime(2025, 1, 1, 8, 0, 0),
                datetime(2025, 1, 1, 17, 0, 0),
                datetime(2025, 1, 2, 8, 30, 0)
            ]
        })
        
        # Salvar dados de teste
        test_data.to_csv('registro_presenca.csv', index=False)
        
        # Gerar relatório
        start_date = datetime(2025, 1, 1).date()
        end_date = datetime(2025, 1, 2).date()
        
        csv_path, pdf_path = report_generator.generate_period_report(
            start_date, end_date, "teste"
        )
        
        # Verificar se arquivos foram criados
        assert csv_path is not None
        assert Path(csv_path).exists()
        assert pdf_path is not None
        assert Path(pdf_path).exists()
    
    def test_18_report_statistics(self):
        """Testa cálculo de estatísticas de relatório"""
        report_generator = ReportGenerator()
        
        # Criar dados de teste
        test_data = pd.DataFrame({
            'Data': ['2025-01-01', '2025-01-01', '2025-01-02', '2025-01-02'],
            'Hora': ['08:00:00', '17:00:00', '08:30:00', '17:30:00'],
            'Nome': ['João', 'João', 'Maria', 'Maria'],
            'ID_Usuario': ['joao', 'joao', 'maria', 'maria'],
            'Tipo': ['ENTRADA', 'SAÍDA', 'ENTRADA', 'SAÍDA'],
            'Timestamp': [
                datetime(2025, 1, 1, 8, 0, 0),
                datetime(2025, 1, 1, 17, 0, 0),
                datetime(2025, 1, 2, 8, 30, 0),
                datetime(2025, 1, 2, 17, 30, 0)
            ]
        })
        
        # Salvar dados de teste
        test_data.to_csv('registro_presenca.csv', index=False)
        
        # Obter estatísticas
        stats = report_generator.get_attendance_statistics()
        
        # Verificar se estatísticas foram calculadas
        assert stats is not None
        assert 'total_records' in stats
        assert 'unique_users' in stats
        assert 'date_range' in stats
    
    def test_19_user_statistics_update(self):
        """Testa atualização de estatísticas do usuário"""
        user_manager = UserManager()
        
        # Adicionar usuário
        user_manager.add_user("Teste Stats", "teste_stats")
        
        # Atualizar estatísticas
        result = user_manager.update_user_statistics("teste_stats", "ENTRADA")
        assert result is True
        
        # Verificar se estatísticas foram atualizadas
        user = user_manager.get_user("teste_stats")
        assert user['total_entries'] == 1
        assert user['total_exits'] == 0
        assert user['last_seen'] is not None
        
        # Atualizar saída
        result = user_manager.update_user_statistics("teste_stats", "SAÍDA")
        assert result is True
        
        # Verificar estatísticas finais
        user = user_manager.get_user("teste_stats")
        assert user['total_entries'] == 1
        assert user['total_exits'] == 1
    
    def test_20_config_file_operations(self):
        """Testa operações com arquivo de configuração"""
        system = DetfaceSystem()
        
        # Verificar configuração inicial
        assert system.config['max_users'] == 5
        
        # Modificar configuração
        system.config['max_users'] = 10
        system.save_config()
        
        # Recarregar sistema
        new_system = DetfaceSystem()
        assert new_system.config['max_users'] == 10


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"]) 