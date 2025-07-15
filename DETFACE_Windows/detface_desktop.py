#!/usr/bin/env python3
"""
DETFACE - Aplicação Desktop Profissional
Interface gráfica com abas separadas para cada funcionalidade
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import threading
import time
import numpy as np
from collections import deque
from face_detector import FaceDetector
from user_manager import UserManager
from report_generator import ReportGenerator
import os
import csv
from datetime import datetime, timedelta

class DetfaceDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DETFACE - Sistema de Reconhecimento Facial")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f0f0f0")
        
        # Inicializar componentes
        self.face_detector = FaceDetector()
        self.user_manager = UserManager()
        self.report_generator = ReportGenerator()
        
        # Variáveis de controle
        self.camera = None
        self.is_capturing = False
        self.is_recognizing = False
        self.current_frame = None
        self.camera_index = 0
        self.photo_reference = None  # Para manter referência da imagem
        
        # Referências para fotos dos canvas
        self.video_photo = None
        self.register_photo = None
        
        # Variáveis para thread de processamento
        self.processing_thread = None
        self.stop_processing = False
        self.frame_queue = deque(maxlen=3)  # Buffer de frames
        self.processed_faces = []
        self.processing_lock = threading.Lock()
        
        # Variáveis para overlay de reconhecimento
        self.recognition_overlay = None
        self.last_recognition_info = ""
        self.recognition_timer = None
        
        # Configurar interface
        self.setup_ui()
        
        # Tentar inicializar câmera
        self.init_camera()
        
    def process_frames_thread(self):
        """Thread separada para processar frames e detectar faces"""
        last_processing_time = time.time()
        processing_interval = 0.5  # 500ms entre processamentos
        
        while not self.stop_processing:
            try:
                # Aguardar frame disponível
                if len(self.frame_queue) == 0:
                    time.sleep(0.01)  # 10ms
                    continue
                
                current_time = time.time()
                
                # Processar apenas em intervalos regulares
                if current_time - last_processing_time >= processing_interval:
                    # Pegar frame mais recente
                    frame = self.frame_queue[-1]
                    
                    # Detectar faces
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_detector.face_cascade.detectMultiScale(gray, 1.2, 5)
                    
                    # Processar cada face detectada
                    processed_faces = []
                    for (x, y, w, h) in faces:
                        face_roi = gray[y:y+h, x:x+w]
                        
                        # Extrair características da face
                        features = self.face_detector.extract_face_features(face_roi)
                        
                        if features is not None and len(self.face_detector.known_face_features) > 0:
                            # Comparar com faces conhecidas
                            from sklearn.metrics.pairwise import cosine_similarity
                            similarities = []
                            for known_features in self.face_detector.known_face_features:
                                similarity = cosine_similarity([features], [known_features])[0][0]
                                similarities.append(similarity)
                            
                            # Encontrar melhor correspondência
                            best_match_idx = np.argmax(similarities)
                            best_similarity = similarities[best_match_idx]
                            
                            if best_similarity > self.face_detector.recognition_threshold:
                                name = self.face_detector.known_face_names[best_match_idx]
                                user_id = self.face_detector.known_face_ids[best_match_idx]
                                
                                # Verificar cooldown
                                if (user_id not in self.face_detector.last_recognition_time or 
                                    current_time - self.face_detector.last_recognition_time[user_id] > 
                                    self.face_detector.recognition_cooldown):
                                    
                                    # Registrar presença
                                    self.face_detector.register_attendance(user_id, name)
                                    self.face_detector.last_recognition_time[user_id] = current_time
                                    
                                    # Determinar tipo de entrada/saída
                                    attendance_type = self.face_detector.determine_attendance_type(user_id, datetime.now())
                                    
                                    # Atualizar log na thread principal
                                    self.root.after(0, lambda: self.add_to_recognition_log(f"✅ {attendance_type.upper()}: {name} ({best_similarity:.2f})"))
                                    self.root.after(0, self.update_statistics)
                                    
                                    # Mostrar overlay de reconhecimento
                                    overlay_message = f"✅ {attendance_type.upper()}: {name}"
                                    self.root.after(0, lambda: self.show_recognition_overlay(overlay_message, 3))
                                
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
        
    def setup_ui(self):
        """Configura a interface principal"""
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="DETFACE - Sistema de Reconhecimento Facial", 
                              font=("Arial", 20, "bold"), fg="#2c3e50", bg="#f0f0f0")
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Controle de Presença e Permanência", 
                                 font=("Arial", 12), fg="#7f8c8d", bg="#f0f0f0")
        subtitle_label.pack()
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Criar abas
        self.create_recognition_tab()
        self.create_register_tab()
        self.create_admin_tab()
        self.create_reports_tab()
        
        # Status bar
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Sistema iniciado - Verificando câmera...")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)
        
    def create_recognition_tab(self):
        """Cria aba de reconhecimento facial"""
        recognition_frame = ttk.Frame(self.notebook)
        self.notebook.add(recognition_frame, text="🎯 Reconhecimento")
        
        # Frame principal dividido
        main_container = ttk.Frame(recognition_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame esquerdo - Câmera
        camera_frame = ttk.LabelFrame(main_container, text="Visualização da Câmera", padding=10)
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Canvas para vídeo
        self.video_canvas = tk.Canvas(camera_frame, width=640, height=480, bg="black")
        self.video_canvas.pack(pady=(0, 10))
        
        # Botões da câmera
        camera_controls = ttk.Frame(camera_frame)
        camera_controls.pack(fill=tk.X)
        
        self.start_camera_btn = ttk.Button(camera_controls, text="📹 Iniciar Câmera", 
                                          command=self.start_camera)
        self.start_camera_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_camera_btn = ttk.Button(camera_controls, text="⏹️ Parar Câmera", 
                                         command=self.stop_camera, state=tk.DISABLED)
        self.stop_camera_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.recognize_btn = ttk.Button(camera_controls, text="🎯 Iniciar Reconhecimento", 
                                       command=self.toggle_recognition, state=tk.DISABLED)
        self.recognize_btn.pack(side=tk.LEFT)
        
        # Frame direito - Informações
        info_frame = ttk.LabelFrame(main_container, text="Informações de Reconhecimento", padding=10)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Status do reconhecimento
        self.recognition_status = tk.StringVar(value="Parado")
        ttk.Label(info_frame, text="Status:").pack(anchor=tk.W)
        status_label = ttk.Label(info_frame, textvariable=self.recognition_status, 
                                font=("Arial", 12, "bold"))
        status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Log de reconhecimentos em tempo real
        ttk.Label(info_frame, text="Últimos Reconhecimentos:").pack(anchor=tk.W)
        
        self.recognition_log = tk.Text(info_frame, height=20, width=40, font=("Consolas", 10))
        log_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.recognition_log.yview)
        self.recognition_log.configure(yscrollcommand=log_scrollbar.set)
        
        self.recognition_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botão para limpar log
        ttk.Button(info_frame, text="🗑️ Limpar Log", 
                  command=self.clear_recognition_log).pack(pady=(10, 0))
        
    def create_register_tab(self):
        """Cria aba de cadastro de usuários"""
        register_frame = ttk.Frame(self.notebook)
        self.notebook.add(register_frame, text="👤 Cadastrar Usuário")
        
        main_container = ttk.Frame(register_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame esquerdo - Preview da câmera
        preview_frame = ttk.LabelFrame(main_container, text="Preview da Câmera", padding=10)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.register_canvas = tk.Canvas(preview_frame, width=480, height=360, bg="black")
        self.register_canvas.pack(pady=(0, 10))
        
        # Botão para capturar
        capture_controls = ttk.Frame(preview_frame)
        capture_controls.pack(fill=tk.X)
        
        self.capture_btn = ttk.Button(capture_controls, text="📷 Capturar Foto", 
                                     command=self.capture_for_registration, state=tk.DISABLED)
        self.capture_btn.pack()
        
        # Frame direito - Formulário
        form_frame = ttk.LabelFrame(main_container, text="Dados do Usuário", padding=20)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Campos do formulário
        ttk.Label(form_frame, text="Nome Completo:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(form_frame, font=("Arial", 12), width=25)
        self.name_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(form_frame, text="ID do Usuário (opcional):", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.id_entry = ttk.Entry(form_frame, font=("Arial", 12), width=25)
        self.id_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(form_frame, text="Departamento (opcional):", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.dept_entry = ttk.Entry(form_frame, font=("Arial", 12), width=25)
        self.dept_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(form_frame, text="Cargo (opcional):", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.position_entry = ttk.Entry(form_frame, font=("Arial", 12), width=25)
        self.position_entry.pack(fill=tk.X, pady=(0, 20))
        
        # Botão de cadastro
        self.register_btn = ttk.Button(form_frame, text="✅ Cadastrar Usuário", 
                                      command=self.register_user, state=tk.DISABLED)
        self.register_btn.pack(fill=tk.X, pady=(0, 15))
        
        # Instruções
        instructions_frame = ttk.LabelFrame(form_frame, text="Instruções", padding=10)
        instructions_frame.pack(fill=tk.X, pady=(10, 0))
        
        instructions_text = """1. Preencha os dados do usuário
2. Posicione o rosto na câmera
3. Clique em 'Capturar Foto'
4. Verifique se a face foi detectada
5. Clique em 'Cadastrar Usuário'"""
        
        ttk.Label(instructions_frame, text=instructions_text, 
                 justify=tk.LEFT, font=("Arial", 10)).pack(anchor=tk.W)
        
    def create_admin_tab(self):
        """Cria aba administrativa"""
        admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(admin_frame, text="🔧 Administração")
        
        main_container = ttk.Frame(admin_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame superior - Estatísticas
        stats_frame = ttk.LabelFrame(main_container, text="Estatísticas do Sistema", padding=15)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        stats_container = ttk.Frame(stats_frame)
        stats_container.pack(fill=tk.X)
        
        # Estatísticas
        self.total_users_var = tk.StringVar(value="0")
        self.total_records_var = tk.StringVar(value="0")
        self.today_records_var = tk.StringVar(value="0")
        
        ttk.Label(stats_container, text="Total de Usuários:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(stats_container, textvariable=self.total_users_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W, padx=(0, 30))
        
        ttk.Label(stats_container, text="Total de Registros:", font=("Arial", 12)).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        ttk.Label(stats_container, textvariable=self.total_records_var, font=("Arial", 12, "bold")).grid(row=0, column=3, sticky=tk.W, padx=(0, 30))
        
        ttk.Label(stats_container, text="Registros Hoje:", font=("Arial", 12)).grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        ttk.Label(stats_container, textvariable=self.today_records_var, font=("Arial", 12, "bold")).grid(row=0, column=5, sticky=tk.W)
        
        # Botão para atualizar estatísticas
        ttk.Button(stats_frame, text="🔄 Atualizar Estatísticas", 
                  command=self.update_statistics).pack(pady=(10, 0))
        
        # Frame principal - Lista de usuários
        users_frame = ttk.LabelFrame(main_container, text="Gerenciar Usuários", padding=15)
        users_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra de pesquisa
        search_frame = ttk.Frame(users_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Pesquisar:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.search_entry.bind('<KeyRelease>', self.filter_users)
        
        ttk.Button(search_frame, text="🔍 Buscar", 
                  command=self.filter_users).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(search_frame, text="🔄 Recarregar", 
                  command=self.refresh_users_list).pack(side=tk.LEFT)
        
        # Treeview para lista de usuários
        columns = ("id", "name", "dept", "position", "date", "records")
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show="headings", height=15)
        
        # Configurar colunas
        self.users_tree.heading("id", text="ID")
        self.users_tree.heading("name", text="Nome")
        self.users_tree.heading("dept", text="Departamento")
        self.users_tree.heading("position", text="Cargo")
        self.users_tree.heading("date", text="Data Cadastro")
        self.users_tree.heading("records", text="Registros")
        
        self.users_tree.column("id", width=100)
        self.users_tree.column("name", width=200)
        self.users_tree.column("dept", width=150)
        self.users_tree.column("position", width=150)
        self.users_tree.column("date", width=120)
        self.users_tree.column("records", width=80)
        
        # Scrollbar para a lista
        users_scrollbar = ttk.Scrollbar(users_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=users_scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões de ação
        actions_frame = ttk.Frame(users_frame)
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(actions_frame, text="👁️ Ver Detalhes", 
                  command=self.view_user_details).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="✏️ Editar", 
                  command=self.edit_user).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="🗑️ Excluir", 
                  command=self.delete_user).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Button(actions_frame, text="📊 Exportar Lista", 
                  command=self.export_users).pack(side=tk.RIGHT)
        
        # Carregar lista inicial
        self.refresh_users_list()
        self.update_statistics()
        
    def create_reports_tab(self):
        """Cria aba de relatórios"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="📊 Relatórios")
        
        main_container = ttk.Frame(reports_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame esquerdo - Opções de relatório
        options_frame = ttk.LabelFrame(main_container, text="Gerar Relatórios", padding=20)
        options_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Relatórios predefinidos
        ttk.Label(options_frame, text="Relatórios Rápidos:", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Button(options_frame, text="📅 Relatório de Hoje", 
                  command=self.generate_daily_report, width=25).pack(fill=tk.X, pady=2)
        
        # Separador
        ttk.Separator(options_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # Relatório personalizado
        ttk.Label(options_frame, text="Relatório Personalizado:", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 15))
        
        ttk.Label(options_frame, text="Data Inicial:").pack(anchor=tk.W)
        self.start_date_entry = ttk.Entry(options_frame, width=25)
        self.start_date_entry.pack(fill=tk.X, pady=(0, 10))
        self.start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(options_frame, text="Data Final:").pack(anchor=tk.W)
        self.end_date_entry = ttk.Entry(options_frame, width=25)
        self.end_date_entry.pack(fill=tk.X, pady=(0, 10))
        self.end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(options_frame, text="📋 Gerar Relatório Personalizado", 
                  command=self.generate_custom_report, width=25).pack(fill=tk.X, pady=10)
        
        # Frame direito - Visualização de dados
        preview_frame = ttk.LabelFrame(main_container, text="Visualização de Dados", padding=15)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Área de texto para mostrar dados
        self.report_text = tk.Text(preview_frame, font=("Consolas", 10), wrap=tk.WORD)
        report_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scrollbar.set)
        
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Carregar dados iniciais
        self.load_recent_data()
        
    def init_camera(self):
        """Inicializa a câmera"""
        for i in range(5):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        cap.release()
                        self.camera_index = i
                        self.update_status(f"Câmera encontrada no índice {i}")
                        self.start_camera_btn.config(state=tk.NORMAL)
                        return True
                    cap.release()
            except:
                continue
        
        self.update_status("Nenhuma câmera encontrada - Funcionalidades limitadas")
        return False
        
    def start_camera(self):
        """Inicia captura da câmera"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if self.camera.isOpened():
                # Configurar câmera para melhor performance
                self.camera.set(cv2.CAP_PROP_FPS, 30)
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
                
                self.is_capturing = True
                self.start_camera_btn.config(state=tk.DISABLED)
                self.stop_camera_btn.config(state=tk.NORMAL)
                self.recognize_btn.config(state=tk.NORMAL)
                self.capture_btn.config(state=tk.NORMAL)
                self.register_btn.config(state=tk.NORMAL)
                
                # Iniciar thread de captura
                self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
                self.capture_thread.start()
                
                # Iniciar atualização de display
                self.update_display()
                
                self.update_status("Câmera iniciada com sucesso")
                self.add_to_recognition_log("📹 Câmera iniciada")
            else:
                messagebox.showerror("Erro", "Não foi possível iniciar a câmera")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar câmera: {str(e)}")
            
    def stop_camera(self):
        """Para a captura da câmera"""
        self.is_capturing = False
        self.is_recognizing = False
        
        # Parar thread de processamento
        self.stop_processing = True
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)
        
        if self.camera:
            self.camera.release()
            self.camera = None
            
        self.start_camera_btn.config(state=tk.NORMAL)
        self.stop_camera_btn.config(state=tk.DISABLED)
        self.recognize_btn.config(state=tk.DISABLED, text="🎯 Iniciar Reconhecimento")
        self.capture_btn.config(state=tk.DISABLED)
        self.register_btn.config(state=tk.DISABLED)
        self.recognition_status.set("Parado")
        
        # Limpar canvas
        self.video_canvas.delete("all")
        self.video_canvas.create_text(320, 240, text="Câmera Parada", fill="white", font=("Arial", 16))
        
        self.register_canvas.delete("all")
        self.register_canvas.create_text(240, 180, text="Câmera Parada", fill="white", font=("Arial", 14))
        
        # Limpar overlay
        self.clear_recognition_overlay()
        
        self.update_status("Câmera parada")
        self.add_to_recognition_log("⏹️ Câmera parada")
        
    def capture_loop(self):
        """Loop principal de captura de frames"""
        while self.is_capturing and self.camera:
            ret, frame = self.camera.read()
            if ret:
                self.current_frame = frame.copy()
                
                # Adicionar frame à fila de processamento (apenas se reconhecimento ativo)
                if self.is_recognizing:
                    self.frame_queue.append(frame.copy())
                

                
            time.sleep(0.03)  # ~30 FPS

    def display_frame_on_canvas(self, frame, canvas, size):
        """Exibe frame no canvas especificado"""
        try:
            # Redimensionar frame
            frame_resized = cv2.resize(frame, size)
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            # Converter para PIL
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            # Atualizar canvas de forma mais eficiente
            canvas.delete("all")
            canvas.create_image(size[0]//2, size[1]//2, image=photo)
            
            # Manter referência para evitar garbage collection
            if canvas == self.video_canvas:
                self.video_photo = photo
            elif canvas == self.register_canvas:
                self.register_photo = photo
            
        except Exception as e:
            print(f"Erro ao exibir frame: {e}")


        
    def show_recognition_overlay(self, message, duration=3):
        """Mostra overlay de reconhecimento na interface"""
        # Cancelar timer anterior se existir
        if self.recognition_timer:
            self.root.after_cancel(self.recognition_timer)
        
        # Criar overlay na interface
        if hasattr(self, 'video_canvas'):
            # Limpar overlay anterior
            self.video_canvas.delete("overlay")
            
            # Criar novo overlay
            self.video_canvas.create_text(
                320, 50,  # Posição no topo
                text=message,
                fill="lime",
                font=("Arial", 14, "bold"),
                tags="overlay"
            )
            
            # Configurar timer para remover overlay
            self.recognition_timer = self.root.after(duration * 1000, self.clear_recognition_overlay)
    
    def clear_recognition_overlay(self):
        """Remove overlay de reconhecimento"""
        if hasattr(self, 'video_canvas'):
            self.video_canvas.delete("overlay")
        self.recognition_timer = None
        
    def update_display(self):
        """Atualiza o display periodicamente"""
        if self.is_capturing and self.current_frame is not None:
            try:
                # Exibir frame limpo
                self.display_frame_on_canvas(self.current_frame, self.video_canvas, (640, 480))
                self.display_frame_on_canvas(self.current_frame, self.register_canvas, (480, 360))
            except Exception as e:
                print(f"Erro ao atualizar display: {e}")
        
        # Agendar próxima atualização
        if self.is_capturing:
            self.root.after(33, self.update_display)  # ~30 FPS
        
    def toggle_recognition(self):
        """Liga/desliga reconhecimento"""
        if not self.is_recognizing:
            self.is_recognizing = True
            self.recognize_btn.config(text="⏹️ Parar Reconhecimento")
            self.recognition_status.set("🔴 Ativo")
            self.update_status("Reconhecimento facial ativo")
            self.add_to_recognition_log("🎯 Reconhecimento iniciado")
            
            # Iniciar thread de processamento
            self.stop_processing = False
            self.processing_thread = threading.Thread(target=self.process_frames_thread, daemon=True)
            self.processing_thread.start()
        else:
            self.is_recognizing = False
            self.recognize_btn.config(text="🎯 Iniciar Reconhecimento")
            self.recognition_status.set("⚫ Parado")
            self.update_status("Reconhecimento facial parado")
            self.add_to_recognition_log("⏸️ Reconhecimento parado")
            
            # Parar thread de processamento
            self.stop_processing = True
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=1.0)
            
    def capture_for_registration(self):
        """Captura frame para cadastro"""
        if self.current_frame is not None:
            # Verificar se há faces detectadas
            gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                messagebox.showinfo("Sucesso", f"Face detectada! {len(faces)} face(s) encontrada(s).\nPreencha os dados e clique em 'Cadastrar Usuário'.")
                self.register_btn.config(state=tk.NORMAL)
            else:
                messagebox.showwarning("Aviso", "Nenhuma face detectada na imagem!\nPosicione seu rosto na câmera e tente novamente.")
        else:
            messagebox.showerror("Erro", "Nenhum frame disponível da câmera!")
            
    def register_user(self):
        """Registra novo usuário"""
        name = self.name_entry.get().strip()
        user_id = self.id_entry.get().strip()
        department = self.dept_entry.get().strip()
        position = self.position_entry.get().strip()
        
        if not name:
            messagebox.showerror("Erro", "Nome é obrigatório!")
            return
            
        if not user_id:
            user_id = name.lower().replace(" ", "_")
            
        if self.current_frame is None:
            messagebox.showerror("Erro", "Nenhum frame disponível da câmera!")
            return
            
        try:
            # Verificar se usuário já existe
            existing_users = self.user_manager.get_all_users()
            if any(user['id'] == user_id for user in existing_users):
                messagebox.showerror("Erro", f"Usuário com ID '{user_id}' já existe!")
                return
            
            # Salvar imagem
            filename = f"faces/{user_id}.jpg"
            cv2.imwrite(filename, self.current_frame)
            
            # Validar e cadastrar usuário
            if self.face_detector.validate_captured_image(filename):
                # Preparar dados adicionais
                additional_info = {}
                if department:
                    additional_info['department'] = department
                if position:
                    additional_info['position'] = position
                
                self.user_manager.add_user(name, user_id, additional_info)
                self.face_detector.load_known_faces()
                
                messagebox.showinfo("Sucesso", f"Usuário '{name}' cadastrado com sucesso!")
                
                # Limpar campos
                self.name_entry.delete(0, tk.END)
                self.id_entry.delete(0, tk.END)
                self.dept_entry.delete(0, tk.END)
                self.position_entry.delete(0, tk.END)
                
                self.register_btn.config(state=tk.DISABLED)
                self.refresh_users_list()
                self.update_statistics()
                self.add_to_recognition_log(f"👤 Usuário cadastrado: {name}")
            else:
                os.remove(filename)
                messagebox.showerror("Erro", "Nenhuma face válida detectada na imagem!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {str(e)}")

    def refresh_users_list(self):
        """Atualiza lista de usuários"""
        # Limpar lista
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        # Carregar usuários
        users = self.user_manager.get_all_users()
        for user in users:
            # Contar registros do usuário
            record_count = self.count_user_records(user['id'])
            
            # Obter dados adicionais
            dept = user.get('department', '-')
            position = user.get('position', '-')
            
            self.users_tree.insert("", tk.END, values=(
                user['id'], 
                user['name'], 
                dept,
                position,
                user['registered_date'], 
                record_count
            ))

    def count_user_records(self, user_id):
        """Conta registros de presença de um usuário"""
        try:
            if not os.path.exists("registro_presenca.csv"):
                return 0
            
            count = 0
            with open("registro_presenca.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] == user_id:
                        count += 1
            return count
        except:
            return 0

    def filter_users(self, event=None):
        """Filtra usuários na lista"""
        search_term = self.search_entry.get().lower()
        
        # Limpar lista
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        # Carregar usuários filtrados
        users = self.user_manager.get_all_users()
        for user in users:
            if (search_term in user['name'].lower() or 
                search_term in user['id'].lower() or
                search_term in user.get('department', '').lower() or
                search_term in user.get('position', '').lower()):
                
                record_count = self.count_user_records(user['id'])
                dept = user.get('department', '-')
                position = user.get('position', '-')
                
                self.users_tree.insert("", tk.END, values=(
                    user['id'], 
                    user['name'], 
                    dept,
                    position,
                    user['registered_date'], 
                    record_count
                ))

    def view_user_details(self):
        """Exibe detalhes do usuário selecionado"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um usuário para ver detalhes")
            return
            
        item = self.users_tree.item(selection[0])
        user_id = str(item['values'][0])  # Converter para string
        
        # Criar janela de detalhes
        self.show_user_details_window(user_id)

    def show_user_details_window(self, user_id):
        """Mostra janela com detalhes do usuário"""
        user_data = self.user_manager.get_user(user_id)
        
        if not user_data:
            messagebox.showerror("Erro", f"Usuário com ID '{user_id}' não encontrado!")
            return
        
        # Criar janela
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Detalhes - {user_data['name']}")
        details_window.geometry("600x500")
        details_window.resizable(False, False)
        
        # Frame principal
        main_frame = ttk.Frame(details_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informações do usuário
        info_frame = ttk.LabelFrame(main_frame, text="Informações do Usuário", padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(info_frame, text="Nome:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(info_frame, text=user_data['name'], font=("Arial", 12)).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(info_frame, text="ID:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        ttk.Label(info_frame, text=user_data['id'], font=("Arial", 12)).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(info_frame, text="Departamento:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        ttk.Label(info_frame, text=user_data.get('department', 'Não informado'), font=("Arial", 12)).grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(info_frame, text="Cargo:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        ttk.Label(info_frame, text=user_data.get('position', 'Não informado'), font=("Arial", 12)).grid(row=3, column=1, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(info_frame, text="Data Cadastro:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        ttk.Label(info_frame, text=user_data['registered_date'], font=("Arial", 12)).grid(row=4, column=1, sticky=tk.W, pady=(5, 0))
        
        # Histórico de registros
        history_frame = ttk.LabelFrame(main_frame, text="Últimos Registros de Presença", padding=15)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de registros
        columns = ("date", "time", "type")
        history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        
        history_tree.heading("date", text="Data")
        history_tree.heading("time", text="Hora")
        history_tree.heading("type", text="Tipo")
        
        history_tree.column("date", width=120)
        history_tree.column("time", width=100)
        history_tree.column("type", width=100)
        
        # Carregar registros do usuário
        self.load_user_records(history_tree, user_id)
        
        history_tree.pack(fill=tk.BOTH, expand=True)
        
        # Botão fechar
        ttk.Button(main_frame, text="Fechar", command=details_window.destroy).pack(pady=(15, 0))

    def load_user_records(self, tree, user_id):
        """Carrega registros de presença do usuário"""
        try:
            if not os.path.exists("registro_presenca.csv"):
                return
            
            records = []
            with open("registro_presenca.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['user_id'] == user_id:
                        records.append(row)
            
            # Mostrar últimos 50 registros
            for record in records[-50:]:
                timestamp = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S')
                tree.insert("", 0, values=(
                    timestamp.strftime('%d/%m/%Y'),
                    timestamp.strftime('%H:%M:%S'),
                    record['type'].upper()
                ))
                
        except Exception as e:
            print(f"Erro ao carregar registros: {e}")

    def edit_user(self):
        """Edita usuário selecionado"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um usuário para editar")
            return
            
        item = self.users_tree.item(selection[0])
        user_id = str(item['values'][0])  # Converter para string
        
        self.show_edit_user_window(user_id)

    def show_edit_user_window(self, user_id):
        """Mostra janela de edição do usuário"""
        user_data = self.user_manager.get_user(user_id)
        
        if not user_data:
            messagebox.showerror("Erro", f"Usuário com ID '{user_id}' não encontrado!")
            return
        
        # Criar janela
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Editar - {user_data['name']}")
        edit_window.geometry("400x350")
        edit_window.resizable(False, False)
        
        # Frame principal
        main_frame = ttk.Frame(edit_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos de edição
        ttk.Label(main_frame, text="Nome:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        name_var = tk.StringVar(value=user_data['name'])
        name_entry = ttk.Entry(main_frame, textvariable=name_var, font=("Arial", 12), width=30)
        name_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(main_frame, text="Departamento:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        dept_var = tk.StringVar(value=user_data.get('department', ''))
        dept_entry = ttk.Entry(main_frame, textvariable=dept_var, font=("Arial", 12), width=30)
        dept_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(main_frame, text="Cargo:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 5))
        position_var = tk.StringVar(value=user_data.get('position', ''))
        position_entry = ttk.Entry(main_frame, textvariable=position_var, font=("Arial", 12), width=30)
        position_entry.pack(fill=tk.X, pady=(0, 20))
        
        def save_changes():
            try:
                new_name = name_var.get().strip()
                new_dept = dept_var.get().strip()
                new_position = position_var.get().strip()
                
                if not new_name:
                    messagebox.showerror("Erro", "Nome é obrigatório!")
                    return
                
                # Atualizar dados
                update_data = {'name': new_name}
                if new_dept:
                    update_data['department'] = new_dept
                if new_position:
                    update_data['position'] = new_position
                
                success = self.user_manager.update_user(user_id, **update_data)
                
                if success:
                    self.face_detector.load_known_faces()  # Recarregar nomes
                    messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
                    edit_window.destroy()
                    self.refresh_users_list()
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar usuário!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")
        
        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Salvar", command=save_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Cancelar", command=edit_window.destroy).pack(side=tk.LEFT)

    def delete_user(self):
        """Exclui usuário selecionado"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um usuário para excluir")
            return
            
        item = self.users_tree.item(selection[0])
        user_id = str(item['values'][0])  # Converter para string
        user_name = item['values'][1]
        
        # Confirmar exclusão
        if messagebox.askyesno("Confirmar Exclusão", 
                              f"Tem certeza que deseja excluir o usuário '{user_name}'?\n\n"
                              f"Esta ação não pode ser desfeita e removerá:\n"
                              f"- Dados do usuário\n"
                              f"- Foto facial cadastrada\n"
                              f"- Não afetará o histórico de registros"):
            
            try:
                success = self.user_manager.remove_user(user_id)
                
                if success:
                    self.face_detector.load_known_faces()
                    self.refresh_users_list()
                    self.update_statistics()
                    
                    messagebox.showinfo("Sucesso", f"Usuário '{user_name}' excluído com sucesso!")
                    self.add_to_recognition_log(f"🗑️ Usuário excluído: {user_name}")
                else:
                    messagebox.showerror("Erro", "Falha ao excluir usuário!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir usuário: {str(e)}")

    def export_users(self):
        """Exporta lista de usuários"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Salvar lista de usuários"
            )
            
            if filename:
                users = self.user_manager.get_all_users()
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['id', 'name', 'department', 'position', 'registered_date', 'total_records']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for user in users:
                        writer.writerow({
                            'id': user['id'],
                            'name': user['name'],
                            'department': user.get('department', ''),
                            'position': user.get('position', ''),
                            'registered_date': user['registered_date'],
                            'total_records': self.count_user_records(user['id'])
                        })
                
                messagebox.showinfo("Sucesso", f"Lista exportada para: {filename}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")

    def update_statistics(self):
        """Atualiza estatísticas do sistema"""
        try:
            # Total de usuários
            users = self.user_manager.get_all_users()
            self.total_users_var.set(str(len(users)))
            
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
            
            self.total_records_var.set(str(total_records))
            self.today_records_var.set(str(today_records))
            
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")

    def generate_daily_report(self):
        """Gera relatório do dia"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            self.generate_report_for_period(today, today, "Diário")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório diário: {str(e)}")

    def generate_weekly_report(self):
        """Gera relatório semanal"""
        try:
            csv_file, pdf_file = self.report_generator.generate_weekly_report()
            messagebox.showinfo("Sucesso", f"Relatório semanal gerado:\nCSV: {csv_file}\nPDF: {pdf_file}")
            self.add_to_recognition_log("📊 Relatório semanal gerado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório semanal: {str(e)}")

    def generate_monthly_report(self):
        """Gera relatório mensal"""
        try:
            csv_file, pdf_file = self.report_generator.generate_monthly_report()
            messagebox.showinfo("Sucesso", f"Relatório mensal gerado:\nCSV: {csv_file}\nPDF: {pdf_file}")
            self.add_to_recognition_log("📈 Relatório mensal gerado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório mensal: {str(e)}")

    def generate_custom_report(self):
        """Gera relatório personalizado"""
        try:
            start_date = self.start_date_entry.get().strip()
            end_date = self.end_date_entry.get().strip()
            
            if not start_date or not end_date:
                messagebox.showerror("Erro", "Preencha as datas de início e fim!")
                return
            
            self.generate_report_for_period(start_date, end_date, "Personalizado")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório personalizado: {str(e)}")

    def generate_report_for_period(self, start_date, end_date, report_type):
        """Gera relatório para período específico"""
        try:
            # Carregar dados do período
            records = []
            if os.path.exists("registro_presenca.csv"):
                with open("registro_presenca.csv", 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        record_date = row['timestamp'][:10]  # YYYY-MM-DD
                        if start_date <= record_date <= end_date:
                            records.append(row)
            
            # Exibir dados na área de preview
            self.display_report_data(records, start_date, end_date, report_type)
            
        except Exception as e:
            raise e

    def display_report_data(self, records, start_date, end_date, report_type):
        """Exibe dados do relatório na área de preview"""
        self.report_text.delete(1.0, tk.END)
        
        # Cabeçalho
        header = f"RELATÓRIO {report_type.upper()}\n"
        header += f"Período: {start_date} a {end_date}\n"
        header += f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        header += "=" * 60 + "\n\n"
        
        self.report_text.insert(tk.END, header)
        
        if not records:
            self.report_text.insert(tk.END, "Nenhum registro encontrado para o período selecionado.\n")
            return
        
        # Resumo
        total_records = len(records)
        unique_users = len(set(record['user_id'] for record in records))
        
        summary = f"RESUMO:\n"
        summary += f"Total de registros: {total_records}\n"
        summary += f"Usuários únicos: {unique_users}\n\n"
        
        self.report_text.insert(tk.END, summary)
        
        # Detalhes por usuário
        user_records = {}
        for record in records:
            user_id = record['user_id']
            if user_id not in user_records:
                user_records[user_id] = []
            user_records[user_id].append(record)
        
        self.report_text.insert(tk.END, "DETALHES POR USUÁRIO:\n" + "-" * 30 + "\n")
        
        for user_id, user_records_list in user_records.items():
            user_name = user_records_list[0]['name']
            
            self.report_text.insert(tk.END, f"\n{user_name} (ID: {user_id}):\n")
            
            for record in user_records_list[-10:]:  # Últimos 10 registros
                timestamp = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S')
                self.report_text.insert(tk.END, 
                    f"  {timestamp.strftime('%d/%m/%Y %H:%M:%S')} - {record['type'].upper()}\n")
            
            if len(user_records_list) > 10:
                self.report_text.insert(tk.END, f"  ... e mais {len(user_records_list) - 10} registros\n")

    def load_recent_data(self):
        """Carrega dados recentes na aba de relatórios"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Carregar dados dos últimos 2 dias
            records = []
            if os.path.exists("registro_presenca.csv"):
                with open("registro_presenca.csv", 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        record_date = row['timestamp'][:10]
                        if record_date >= yesterday:
                            records.append(row)
            
            self.display_report_data(records, yesterday, today, "Últimos Dias")
            
        except Exception as e:
            self.report_text.insert(tk.END, f"Erro ao carregar dados: {str(e)}")

    def add_to_recognition_log(self, message):
        """Adiciona mensagem ao log de reconhecimento"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.recognition_log.insert(tk.END, log_message)
        self.recognition_log.see(tk.END)
        
        # Manter apenas últimas 100 linhas
        lines = self.recognition_log.get(1.0, tk.END).split('\n')
        if len(lines) > 100:
            self.recognition_log.delete(1.0, f"{len(lines) - 100}.0")

    def clear_recognition_log(self):
        """Limpa o log de reconhecimento"""
        self.recognition_log.delete(1.0, tk.END)
        self.add_to_recognition_log("Log limpo")

    def update_status(self, message):
        """Atualiza barra de status"""
        self.status_var.set(f"{datetime.now().strftime('%H:%M:%S')} - {message}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DetfaceDesktopApp(root)
    root.mainloop()