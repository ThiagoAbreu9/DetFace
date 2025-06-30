#!/usr/bin/env python3
"""
DETFACE - Módulo de Detecção e Reconhecimento Facial
Responsável por capturar, processar e reconhecer rostos usando OpenCV e face_recognition
"""

import cv2
import face_recognition
import numpy as np
import os
import json
import datetime
import csv
from pathlib import Path
import time

class FaceDetector:
    """Classe responsável pela detecção e reconhecimento facial"""
    
    def __init__(self):
        """Inicializa o detector facial"""
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.recognition_threshold = 0.6
        self.last_recognition_time = {}
        self.recognition_cooldown = 5  # segundos entre reconhecimentos do mesmo usuário
        
        # Carregar rostos conhecidos
        self.load_known_faces()
        
    def load_known_faces(self):
        """Carrega todas as faces conhecidas da pasta faces/"""
        faces_dir = Path("faces")
        if not faces_dir.exists():
            faces_dir.mkdir()
            return
            
        print("🔄 Carregando rostos cadastrados...")
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        # Procurar por arquivos de imagem
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        for image_file in faces_dir.iterdir():
            if image_file.suffix.lower() in image_extensions:
                try:
                    # Carregar imagem
                    image = face_recognition.load_image_file(str(image_file))
                    
                    # Encontrar encodings das faces na imagem
                    face_encodings = face_recognition.face_encodings(image)
                    
                    if face_encodings:
                        # Usar apenas a primeira face encontrada
                        face_encoding = face_encodings[0]
                        
                        # Extrair nome do arquivo (sem extensão)
                        name = image_file.stem
                        
                        # Tentar carregar metadados do usuário
                        user_data = self.get_user_metadata(name)
                        display_name = user_data.get('name', name) if user_data else name
                        user_id = user_data.get('id', name) if user_data else name
                        
                        self.known_face_encodings.append(face_encoding)
                        self.known_face_names.append(display_name)
                        self.known_face_ids.append(user_id)
                        
                        print(f"✅ Carregado: {display_name}")
                        
                    else:
                        print(f"⚠️ Nenhuma face encontrada em: {image_file.name}")
                        
                except Exception as e:
                    print(f"❌ Erro ao carregar {image_file.name}: {str(e)}")
                    
        print(f"📊 Total de rostos carregados: {len(self.known_face_encodings)}")
        
    def get_user_metadata(self, user_id):
        """Carrega metadados do usuário do arquivo users.json"""
        try:
            with open('users.json', 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                return users_data.get(user_id)
        except FileNotFoundError:
            return None
            
    def check_camera(self):
        """Verifica se a câmera está disponível"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False
            cap.release()
            return True
        except:
            return False
            
    def capture_user_face(self, name, user_id):
        """Captura uma imagem do usuário para cadastro"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Erro: Não foi possível acessar a câmera")
            return False
            
        print("📸 Câmera iniciada. Posicione seu rosto na tela...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Erro ao capturar frame da câmera")
                break
                
            # Espelhar a imagem para melhor experiência do usuário
            frame = cv2.flip(frame, 1)
            
            # Detectar faces no frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            # Desenhar retângulos ao redor das faces detectadas
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "Face detectada - Pressione SPACE", 
                           (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Instruções na tela
            cv2.putText(frame, f"Cadastrando: {name}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "SPACE = Capturar | Q = Cancelar", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.imshow('Cadastro de Usuario - DETFACE', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '):  # Espaço para capturar
                if face_locations:
                    # Salvar a imagem
                    filename = f"faces/{user_id}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"✅ Imagem salva: {filename}")
                    
                    # Validar qualidade da imagem capturada
                    if self.validate_captured_image(filename):
                        cap.release()
                        cv2.destroyAllWindows()
                        return True
                    else:
                        print("⚠️ Qualidade da imagem insuficiente. Tente novamente.")
                        os.remove(filename)
                else:
                    print("❌ Nenhuma face detectada. Posicione-se melhor na câmera.")
                    
            elif key == ord('q'):  # 'q' para cancelar
                break
                
        cap.release()
        cv2.destroyAllWindows()
        return False
        
    def validate_captured_image(self, image_path):
        """Valida a qualidade da imagem capturada"""
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                print("❌ Nenhuma face clara detectada na imagem")
                return False
                
            if len(face_encodings) > 1:
                print("⚠️ Múltiplas faces detectadas. Use uma imagem com apenas uma pessoa.")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Erro na validação: {str(e)}")
            return False
            
    def start_recognition(self):
        """Inicia o processo de reconhecimento facial em tempo real"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Erro: Não foi possível acessar a câmera")
            return
            
        print("🎥 Sistema de reconhecimento ativo...")
        print("💡 Pressione 'q' para sair")
        
        # Configurar resolução da câmera para melhor performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        frame_count = 0
        recognition_start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Erro ao capturar frame")
                break
                
            frame_count += 1
            
            # Espelhar frame para melhor experiência
            frame = cv2.flip(frame, 1)
            
            # Processar apenas a cada 2 frames para melhor performance
            if self.process_this_frame:
                # Redimensionar frame para processamento mais rápido
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Encontrar faces e encodings
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                
                self.face_names = []
                for face_encoding in self.face_encodings:
                    # Comparar com faces conhecidas
                    matches = face_recognition.compare_faces(
                        self.known_face_encodings, face_encoding, tolerance=self.recognition_threshold)
                    name = "Desconhecido"
                    user_id = "unknown"
                    
                    # Usar a face com menor distância
                    face_distances = face_recognition.face_distance(
                        self.known_face_encodings, face_encoding)
                    
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            user_id = self.known_face_ids[best_match_index]
                            
                            # Registrar presença com cooldown
                            self.register_attendance(user_id, name)
                    
                    self.face_names.append(name)
            
            self.process_this_frame = not self.process_this_frame
            
            # Desenhar resultados no frame
            self.draw_recognition_results(frame)
            
            # Exibir informações na tela
            cv2.putText(frame, "DETFACE - Sistema Ativo", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Usuarios cadastrados: {len(self.known_face_names)}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Calcular e exibir FPS
            if frame_count % 30 == 0:
                current_time = time.time()
                fps = 30 / (current_time - recognition_start_time)
                recognition_start_time = current_time
                
            cv2.putText(frame, f"Pressione 'q' para sair", 
                       (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('DETFACE - Reconhecimento Facial', frame)
            
            # Verificar se deve sair
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Sistema de reconhecimento encerrado")
        
    def draw_recognition_results(self, frame):
        """Desenha os resultados do reconhecimento no frame"""
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Escalar de volta as coordenadas (foram reduzidas em 4x)
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Escolher cor baseada no reconhecimento
            if name == "Desconhecido":
                color = (0, 0, 255)  # Vermelho para desconhecidos
                status = "ACESSO NEGADO"
            else:
                color = (0, 255, 0)   # Verde para conhecidos
                status = "ACESSO AUTORIZADO"
            
            # Desenhar retângulo ao redor da face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Desenhar fundo para o texto
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            
            # Adicionar texto
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 20), font, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, status, (left + 6, bottom - 5), font, 0.4, (255, 255, 255), 1)
            
    def register_attendance(self, user_id, name):
        """Registra a presença do usuário"""
        current_time = time.time()
        
        # Verificar cooldown para evitar registros duplicados
        if user_id in self.last_recognition_time:
            time_diff = current_time - self.last_recognition_time[user_id]
            if time_diff < self.recognition_cooldown:
                return  # Muito cedo para registrar novamente
        
        self.last_recognition_time[user_id] = current_time
        
        # Registrar no arquivo CSV
        timestamp = datetime.datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Determinar se é entrada ou saída
        attendance_type = self.determine_attendance_type(user_id, timestamp)
        
        # Escrever no arquivo CSV
        csv_file = "registro_presenca.csv"
        file_exists = os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Escrever cabeçalho se arquivo não existe
            if not file_exists:
                writer.writerow(['Data', 'Hora', 'ID_Usuario', 'Nome', 'Tipo', 'Timestamp'])
            
            writer.writerow([date_str, time_str, user_id, name, attendance_type, timestamp.isoformat()])
        
        print(f"📝 {attendance_type}: {name} - {date_str} {time_str}")
        
    def determine_attendance_type(self, user_id, current_timestamp):
        """Determina se o registro é entrada ou saída baseado no último registro"""
        try:
            # Ler registros existentes
            with open("registro_presenca.csv", 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                user_records = [row for row in reader if row['ID_Usuario'] == user_id]
                
            if not user_records:
                return "ENTRADA"  # Primeira vez do usuário
                
            # Verificar último registro
            last_record = user_records[-1]
            last_type = last_record['Tipo']
            
            # Alternar entre entrada e saída
            return "SAÍDA" if last_type == "ENTRADA" else "ENTRADA"
            
        except FileNotFoundError:
            return "ENTRADA"  # Arquivo não existe, primeira entrada
        except Exception:
            return "ENTRADA"  # Em caso de erro, considerar entrada
