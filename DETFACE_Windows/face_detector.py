#!/usr/bin/env python3
"""
DETFACE - Módulo de Detecção e Reconhecimento Facial
Responsável por capturar, processar e reconhecer rostos usando OpenCV
"""

import cv2
import numpy as np
import os
import json
import datetime
import csv
from pathlib import Path
import time
import threading
from collections import deque
from sklearn.metrics.pairwise import cosine_similarity

class FaceDetector:
    """Classe responsável pela detecção e reconhecimento facial"""
    
    def __init__(self):
        """Inicializa o detector facial"""
        self.known_face_features = []
        self.known_face_names = []
        self.known_face_ids = []
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Carregar configurações
        self.load_config()
        
        self.last_recognition_time = {}
        self.camera_index = 0
        self.camera_backend = None
        
        # Variáveis para thread de processamento
        self.processing_thread = None
        self.stop_processing = False
        self.frame_queue = deque(maxlen=3)  # Buffer de frames
        self.processed_faces = []
        self.processing_lock = threading.Lock()
        
        # Carregar rostos conhecidos
        self.load_known_faces()
        
    def process_frames_thread(self):
        """Thread separada para processar frames e detectar faces"""
        last_processing_time = time.time()
        
        while not self.stop_processing:
            try:
                # Aguardar frame disponível
                if len(self.frame_queue) == 0:
                    time.sleep(0.01)  # 10ms
                    continue
                
                current_time = time.time()
                
                # Processar apenas em intervalos regulares
                if current_time - last_processing_time >= self.processing_interval:
                    # Pegar frame mais recente
                    frame = self.frame_queue[-1]
                    
                    # Detectar faces
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, self.face_detection_scale, self.face_detection_min_neighbors)
                    
                    # Processar cada face detectada
                    processed_faces = []
                    for (x, y, w, h) in faces:
                        face_roi = gray[y:y+h, x:x+w]
                        
                        # Extrair características da face
                        features = self.extract_face_features(face_roi)
                        
                        if features is not None and len(self.known_face_features) > 0:
                            # Comparar com faces conhecidas
                            similarities = []
                            for known_features in self.known_face_features:
                                similarity = cosine_similarity([features], [known_features])[0][0]
                                similarities.append(similarity)
                            
                            # Encontrar melhor correspondência
                            best_match_idx = np.argmax(similarities)
                            best_similarity = similarities[best_match_idx]
                            
                            if best_similarity > self.recognition_threshold:
                                name = self.known_face_names[best_match_idx]
                                user_id = self.known_face_ids[best_match_idx]
                                
                                # Verificar cooldown
                                if (user_id not in self.last_recognition_time or 
                                    current_time - self.last_recognition_time[user_id] > self.recognition_cooldown):
                                    
                                    # Registrar presença
                                    self.register_attendance(user_id, name)
                                    self.last_recognition_time[user_id] = current_time
                                
                                # Armazenar dados da face
                                processed_faces.append({
                                    'bbox': (x, y, w, h),
                                    'name': name,
                                    'similarity': best_similarity,
                                    'color': (0, 255, 0),
                                    'type': 'known'
                                })
                            else:
                                # Face não reconhecida
                                processed_faces.append({
                                    'bbox': (x, y, w, h),
                                    'name': 'Desconhecido',
                                    'similarity': best_similarity,
                                    'color': (0, 0, 255),
                                    'type': 'unknown'
                                })
                        else:
                            # Só mostrar retângulo
                            processed_faces.append({
                                'bbox': (x, y, w, h),
                                'name': '',
                                'similarity': 0,
                                'color': (255, 0, 0),
                                'type': 'detected'
                            })
                    
                    # Atualizar faces processadas
                    with self.processing_lock:
                        self.processed_faces = processed_faces
                    
                    last_processing_time = current_time
                else:
                    time.sleep(0.01)  # 10ms
                    
            except Exception as e:
                print(f"Erro na thread de processamento: {e}")
                time.sleep(0.1)
        
    def load_config(self):
        """Carrega configurações do arquivo config.json"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Configurações de reconhecimento
            self.recognition_threshold = config.get('recognition_threshold', 0.75)
            self.recognition_cooldown = config.get('performance', {}).get('recognition_cooldown', 5)
            
            # Configurações de câmera
            camera_settings = config.get('camera_settings', {})
            self.camera_fps = camera_settings.get('fps', 30)
            self.camera_width = camera_settings.get('width', 640)
            self.camera_height = camera_settings.get('height', 480)
            self.camera_buffer_size = camera_settings.get('buffer_size', 1)
            self.camera_auto_exposure = camera_settings.get('auto_exposure', 0.25)
            
            # Configurações de performance
            performance_settings = config.get('performance', {})
            self.processing_interval = performance_settings.get('processing_interval', 0.1)
            self.face_detection_scale = performance_settings.get('face_detection_scale', 1.1)
            self.face_detection_min_neighbors = performance_settings.get('face_detection_min_neighbors', 4)
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar configurações: {e}. Usando valores padrão.")
            # Valores padrão
            self.recognition_threshold = 0.75
            self.recognition_cooldown = 5
            self.camera_fps = 30
            self.camera_width = 640
            self.camera_height = 480
            self.camera_buffer_size = 1
            self.camera_auto_exposure = 0.25
            self.processing_interval = 0.1
            self.face_detection_scale = 1.1
            self.face_detection_min_neighbors = 4
        
    def extract_face_features(self, face_roi):
        """Extrai características do rosto usando histograma LBP simplificado"""
        try:
            # Redimensionar para tamanho padrão
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Converter para escala de cinza se necessário
            if len(face_roi.shape) == 3:
                face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Calcular histograma
            hist = cv2.calcHist([face_roi], [0], None, [256], [0, 256])
            hist = hist.flatten()
            
            # Normalizar
            hist = hist / (hist.sum() + 1e-10)
            
            return hist
        except Exception as e:
            print(f"Erro ao extrair características: {e}")
            return None
        
    def load_known_faces(self):
        """Carrega todas as faces conhecidas da pasta faces/"""
        faces_dir = Path("faces")
        if not faces_dir.exists():
            faces_dir.mkdir()
            return
            
        print("🔄 Carregando rostos cadastrados...")
        
        self.known_face_features = []
        self.known_face_names = []
        self.known_face_ids = []
        
        # Procurar por arquivos de imagem
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(faces_dir.glob(f"*{ext}"))
        
        for image_file in image_files:
            try:
                # Carregar imagem
                image = cv2.imread(str(image_file))
                if image is None:
                    continue
                
                # Detectar face na imagem
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    # Usar a primeira face encontrada
                    x, y, w, h = faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    
                    # Extrair características
                    features = self.extract_face_features(face_roi)
                    if features is not None:
                        # Extrair nome do arquivo (sem extensão)
                        name = image_file.stem
                        
                        # Tentar carregar metadados do usuário
                        user_data = self.get_user_metadata(name)
                        display_name = user_data.get('name', name) if user_data else name
                        user_id = user_data.get('id', name) if user_data else name
                        
                        self.known_face_features.append(features)
                        self.known_face_names.append(display_name)
                        self.known_face_ids.append(user_id)
                        
                        print(f"✅ Carregado: {display_name}")
                else:
                    print(f"⚠️ Nenhuma face encontrada em: {image_file.name}")
                        
            except Exception as e:
                print(f"❌ Erro ao carregar {image_file.name}: {str(e)}")
                
        print(f"📊 Total de rostos carregados: {len(self.known_face_features)}")
        
    def get_user_metadata(self, user_id):
        """Carrega metadados do usuário do arquivo users.json"""
        try:
            users_file = Path("users.json")
            if users_file.exists():
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                    return users_data.get(user_id, None)
        except Exception as e:
            print(f"Erro ao carregar metadados do usuário {user_id}: {e}")
        return None
        
    def configure_camera(self, cap):
        """Configura a câmera para melhor performance"""
        try:
            # Configurar FPS
            cap.set(cv2.CAP_PROP_FPS, self.camera_fps)
            
            # Configurar buffer para reduzir latência
            cap.set(cv2.CAP_PROP_BUFFERSIZE, self.camera_buffer_size)
            
            # Configurar resolução
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            
            # Configurar exposição automática
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, self.camera_auto_exposure)
            
            return True
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível configurar todas as propriedades da câmera: {e}")
            return False
        
    def check_camera(self):
        """Verifica se a câmera está disponível"""
        # Tentar diferentes índices de câmera
        for camera_index in range(5):
            try:
                cap = cv2.VideoCapture(camera_index)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # Configurar câmera
                        self.configure_camera(cap)
                        cap.release()
                        print(f"✅ Câmera encontrada no índice {camera_index}")
                        self.camera_index = camera_index
                        return True
                    cap.release()
            except Exception as e:
                continue
        
        # Tentar com diferentes backends
        for backend in [cv2.CAP_DSHOW, cv2.CAP_V4L2, cv2.CAP_GSTREAMER]:
            try:
                cap = cv2.VideoCapture(0, backend)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # Configurar câmera
                        self.configure_camera(cap)
                        cap.release()
                        print(f"✅ Câmera encontrada com backend {backend}")
                        self.camera_backend = backend
                        self.camera_index = 0
                        return True
                    cap.release()
            except Exception:
                continue
                
        print("❌ Nenhuma câmera funcional encontrada")
        return False
    
    def capture_user_face(self, name, user_id):
        """Captura uma imagem do usuário para cadastro"""
        print(f"\n📷 Capturando foto para {name}...")
        print("Posicione seu rosto na câmera e pressione ESPAÇO para capturar ou ESC para cancelar")
        
        if self.camera_backend:
            cap = cv2.VideoCapture(self.camera_index, self.camera_backend)
        else:
            cap = cv2.VideoCapture(self.camera_index)
            
        if not cap.isOpened():
            print("❌ Erro: Não foi possível acessar a câmera")
            return False
        
        # Configurar câmera para melhor performance
        self.configure_camera(cap)
            
        captured = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Erro ao capturar frame da câmera")
                break
                
            # Detectar faces no frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, self.face_detection_scale, self.face_detection_min_neighbors)
            
            # Desenhar retângulos ao redor das faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Pressione ESPACO para capturar", (x, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            cv2.imshow('Captura de Face - DETFACE', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # ESPAÇO
                if len(faces) > 0:
                    # Salvar imagem
                    image_path = f"faces/{user_id}.jpg"
                    cv2.imwrite(image_path, frame)
                    
                    # Validar imagem capturada
                    if self.validate_captured_image(image_path):
                        print(f"✅ Foto capturada e salva como {image_path}")
                        captured = True
                    else:
                        print("❌ Imagem capturada não é válida")
                        os.remove(image_path)
                else:
                    print("❌ Nenhuma face detectada! Tente novamente.")
                break
            elif key == 27:  # ESC
                print("❌ Captura cancelada")
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        if captured:
            # Recarregar faces conhecidas
            self.load_known_faces()
            
        return captured
    
    def validate_captured_image(self, image_path):
        """Valida a qualidade da imagem capturada"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False
                
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Verificar se pelo menos uma face foi detectada
            if len(faces) == 0:
                return False
                
            # Verificar tamanho mínimo da face
            x, y, w, h = faces[0]
            if w < 50 or h < 50:
                return False
                
            return True
            
        except Exception as e:
            print(f"Erro na validação da imagem: {e}")
            return False
    
    def start_recognition(self):
        """Inicia o processo de reconhecimento facial em tempo real"""
        print("\n🎥 Iniciando reconhecimento facial...")
        print("Pressione 'q' para sair")
        
        if self.camera_backend:
            cap = cv2.VideoCapture(self.camera_index, self.camera_backend)
        else:
            cap = cv2.VideoCapture(self.camera_index)
            
        if not cap.isOpened():
            print("❌ Erro: Não foi possível acessar a câmera")
            return
        
        # Configurar câmera para melhor performance
        self.configure_camera(cap)
        
        # Iniciar thread de processamento
        self.stop_processing = False
        self.processing_thread = threading.Thread(target=self.process_frames_thread, daemon=True)
        self.processing_thread.start()
        
        print("✅ Thread de processamento iniciada")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Erro ao capturar frame")
                    break
                
                # Adicionar frame à fila de processamento
                self.frame_queue.append(frame.copy())
                
                # Desenhar faces processadas
                with self.processing_lock:
                    for face_info in self.processed_faces:
                        x, y, w, h = face_info['bbox']
                        color = face_info['color']
                        name = face_info['name']
                        similarity = face_info['similarity']
                        
                        # Desenhar retângulo
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        
                        # Desenhar texto se houver nome
                        if name:
                            if face_info['type'] == 'known':
                                text = f"{name} ({similarity:.2f})"
                            else:
                                text = name
                            cv2.putText(frame, text, (x, y-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Mostrar frame
                cv2.imshow('DETFACE - Reconhecimento Facial', frame)
                
                # Verificar se usuário quer sair
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\n⚠️ Interrupção detectada...")
        finally:
            # Parar thread de processamento
            self.stop_processing = True
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=1.0)
            
            cap.release()
            cv2.destroyAllWindows()
            print("🔚 Reconhecimento finalizado")
    
    def register_attendance(self, user_id, name):
        """Registra a presença do usuário"""
        try:
            current_timestamp = datetime.datetime.now()
            
            # Determinar tipo de registro (entrada/saída)
            attendance_type = self.determine_attendance_type(user_id, current_timestamp)
            
            # Criar registro
            attendance_record = {
                'timestamp': current_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': user_id,
                'name': name,
                'type': attendance_type
            }
            
            # Salvar no CSV
            csv_file = 'registro_presenca.csv'
            file_exists = os.path.exists(csv_file)
            
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['timestamp', 'user_id', 'name', 'type']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                    
                writer.writerow(attendance_record)
            
            print(f"✅ {attendance_type.upper()}: {name} - {current_timestamp.strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Erro ao registrar presença: {str(e)}")
    
    def determine_attendance_type(self, user_id, current_timestamp):
        """Determina se o registro é entrada ou saída baseado no último registro"""
        try:
            csv_file = 'registro_presenca.csv'
            if not os.path.exists(csv_file):
                return "entrada"
            
            # Ler registros existentes
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                user_records = [row for row in reader if row['user_id'] == user_id]
            
            if not user_records:
                return "entrada"
            
            # Pegar último registro
            last_record = user_records[-1]
            last_type = last_record['type']
            
            # Alternar entre entrada e saída
            return "saída" if last_type == "entrada" else "entrada"
            
        except Exception as e:
            print(f"Erro ao determinar tipo de presença: {e}")
            return "entrada"