#!/usr/bin/env python3
"""
DETFACE - Aplicação Desktop
Interface gráfica nativa usando tkinter para controle de presença
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import threading
import time
import numpy as np
from face_detector import FaceDetector
from user_manager import UserManager
from report_generator import ReportGenerator
import os
import csv
from datetime import datetime

class DetfaceDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DETFACE - Sistema de Reconhecimento Facial")
        self.root.geometry("1200x800")
        
        # Inicializar componentes
        self.face_detector = FaceDetector()
        self.user_manager = UserManager()
        self.report_generator = ReportGenerator()
        
        # Variáveis de controle
        self.camera = None
        self.is_capturing = False
        self.is_recognizing = False
        self.current_frame = None
        
        # Configurar interface
        self.setup_ui()
        
        # Tentar inicializar câmera
        self.init_camera()
        
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="DETFACE - Sistema de Reconhecimento Facial", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Frame esquerdo - Câmera
        camera_frame = ttk.LabelFrame(main_frame, text="Visualização da Câmera", padding="10")
        camera_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Canvas para vídeo
        self.video_canvas = tk.Canvas(camera_frame, width=640, height=480, bg="black")
        self.video_canvas.pack(pady=(0, 10))
        
        # Botões da câmera
        camera_buttons = ttk.Frame(camera_frame)
        camera_buttons.pack(fill=tk.X)
        
        self.start_camera_btn = ttk.Button(camera_buttons, text="Iniciar Câmera", 
                                          command=self.start_camera)
        self.start_camera_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_camera_btn = ttk.Button(camera_buttons, text="Parar Câmera", 
                                         command=self.stop_camera, state=tk.DISABLED)
        self.stop_camera_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.recognize_btn = ttk.Button(camera_buttons, text="Iniciar Reconhecimento", 
                                       command=self.toggle_recognition, state=tk.DISABLED)
        self.recognize_btn.pack(side=tk.LEFT)
        
        # Frame direito - Controles
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        control_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Notebook para abas
        notebook = ttk.Notebook(control_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba Cadastro
        self.setup_register_tab(notebook)
        
        # Aba Usuários
        self.setup_users_tab(notebook)
        
        # Aba Relatórios
        self.setup_reports_tab(notebook)
        
        # Status bar
        self.status_var = tk.StringVar(value="Sistema iniciado - Câmera não conectada")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def setup_register_tab(self, notebook):
        """Configura aba de cadastro de usuários"""
        register_frame = ttk.Frame(notebook, padding="10")
        notebook.add(register_frame, text="Cadastrar Usuário")
        
        # Campo Nome
        ttk.Label(register_frame, text="Nome Completo:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(register_frame, width=30)
        self.name_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Campo ID
        ttk.Label(register_frame, text="ID do Usuário (opcional):").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.id_entry = ttk.Entry(register_frame, width=30)
        self.id_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botão Capturar
        self.capture_btn = ttk.Button(register_frame, text="Capturar e Cadastrar", 
                                     command=self.capture_user, state=tk.DISABLED)
        self.capture_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Instruções
        instructions = tk.Text(register_frame, height=8, width=40, wrap=tk.WORD)
        instructions.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        instructions.insert(tk.END, 
            "Instruções para cadastro:\n\n"
            "1. Digite o nome completo do usuário\n"
            "2. Opcionalmente, digite um ID personalizado\n"
            "3. Posicione o rosto na câmera\n"
            "4. Clique em 'Capturar e Cadastrar'\n"
            "5. Aguarde a confirmação")
        instructions.config(state=tk.DISABLED)
        
    def setup_users_tab(self, notebook):
        """Configura aba de listagem de usuários"""
        users_frame = ttk.Frame(notebook, padding="10")
        notebook.add(users_frame, text="Usuários")
        
        # Lista de usuários
        self.users_tree = ttk.Treeview(users_frame, columns=("name", "id", "date"), show="headings")
        self.users_tree.heading("name", text="Nome")
        self.users_tree.heading("id", text="ID")
        self.users_tree.heading("date", text="Data Cadastro")
        
        self.users_tree.column("name", width=200)
        self.users_tree.column("id", width=100)
        self.users_tree.column("date", width=150)
        
        self.users_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Botões
        users_buttons = ttk.Frame(users_frame)
        users_buttons.pack(fill=tk.X)
        
        ttk.Button(users_buttons, text="Atualizar Lista", 
                  command=self.refresh_users_list).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(users_buttons, text="Remover Selecionado", 
                  command=self.remove_selected_user).pack(side=tk.LEFT)
        
        # Carregar lista inicial
        self.refresh_users_list()
        
    def setup_reports_tab(self, notebook):
        """Configura aba de relatórios"""
        reports_frame = ttk.Frame(notebook, padding="10")
        notebook.add(reports_frame, text="Relatórios")
        
        ttk.Label(reports_frame, text="Gerar Relatórios:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Botões de relatório
        ttk.Button(reports_frame, text="Relatório Semanal", 
                  command=self.generate_weekly_report, width=25).pack(pady=5)
        ttk.Button(reports_frame, text="Relatório Mensal", 
                  command=self.generate_monthly_report, width=25).pack(pady=5)
        
        # Log de reconhecimentos
        ttk.Label(reports_frame, text="Últimos Reconhecimentos:", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(20, 10))
        
        self.log_text = tk.Text(reports_frame, height=15, width=40)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para o log
        log_scrollbar = ttk.Scrollbar(self.log_text)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)
        
    def init_camera(self):
        """Inicializa a câmera"""
        for i in range(5):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cap.release()
                        self.camera_index = i
                        self.update_status(f"Câmera encontrada no índice {i}")
                        self.start_camera_btn.config(state=tk.NORMAL)
                        return True
                cap.release()
            except:
                continue
        
        self.update_status("Nenhuma câmera encontrada")
        return False
        
    def start_camera(self):
        """Inicia captura da câmera"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if self.camera.isOpened():
                self.is_capturing = True
                self.start_camera_btn.config(state=tk.DISABLED)
                self.stop_camera_btn.config(state=tk.NORMAL)
                self.recognize_btn.config(state=tk.NORMAL)
                self.capture_btn.config(state=tk.NORMAL)
                
                # Iniciar thread de captura
                self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
                self.capture_thread.start()
                
                self.update_status("Câmera iniciada")
            else:
                messagebox.showerror("Erro", "Não foi possível iniciar a câmera")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar câmera: {str(e)}")
            
    def stop_camera(self):
        """Para a captura da câmera"""
        self.is_capturing = False
        self.is_recognizing = False
        
        if self.camera:
            self.camera.release()
            self.camera = None
            
        self.start_camera_btn.config(state=tk.NORMAL)
        self.stop_camera_btn.config(state=tk.DISABLED)
        self.recognize_btn.config(state=tk.DISABLED, text="Iniciar Reconhecimento")
        self.capture_btn.config(state=tk.DISABLED)
        
        # Limpar canvas
        self.video_canvas.delete("all")
        self.video_canvas.create_text(320, 240, text="Câmera Parada", fill="white", font=("Arial", 16))
        
        self.update_status("Câmera parada")
        
    def capture_loop(self):
        """Loop principal de captura de frames"""
        while self.is_capturing and self.camera:
            ret, frame = self.camera.read()
            if ret:
                self.current_frame = frame.copy()
                
                # Processar reconhecimento se ativo
                if self.is_recognizing:
                    frame = self.process_recognition(frame)
                
                # Converter para tkinter
                self.display_frame(frame)
                
            time.sleep(0.03)  # ~30 FPS
            
    def display_frame(self, frame):
        """Exibe frame no canvas"""
        # Redimensionar frame
        frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Converter para PIL
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image)
        
        # Atualizar canvas
        self.video_canvas.delete("all")
        self.video_canvas.create_image(320, 240, image=photo)
        self.video_canvas.image = photo  # Manter referência
        
    def process_recognition(self, frame):
        """Processa reconhecimento facial no frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            features = self.face_detector.extract_face_features(face_roi)
            
            if features is not None and len(self.face_detector.known_face_features) > 0:
                from sklearn.metrics.pairwise import cosine_similarity
                similarities = []
                for known_features in self.face_detector.known_face_features:
                    similarity = cosine_similarity([features], [known_features])[0][0]
                    similarities.append(similarity)
                
                best_match_idx = np.argmax(similarities)
                best_similarity = similarities[best_match_idx]
                
                if best_similarity > self.face_detector.recognition_threshold:
                    name = self.face_detector.known_face_names[best_match_idx]
                    user_id = self.face_detector.known_face_ids[best_match_idx]
                    
                    # Verificar cooldown
                    current_time = time.time()
                    if (user_id not in self.face_detector.last_recognition_time or 
                        current_time - self.face_detector.last_recognition_time[user_id] > 
                        self.face_detector.recognition_cooldown):
                        
                        # Registrar presença
                        self.face_detector.register_attendance(user_id, name)
                        self.face_detector.last_recognition_time[user_id] = current_time
                        
                        # Atualizar log
                        self.add_to_log(f"✅ RECONHECIDO: {name}")
                    
                    # Desenhar retângulo verde
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, f"{name} ({best_similarity:.2f})", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    # Face não reconhecida
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "Desconhecido", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                # Apenas mostrar retângulo
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
        return frame
        
    def toggle_recognition(self):
        """Liga/desliga reconhecimento"""
        if not self.is_recognizing:
            self.is_recognizing = True
            self.recognize_btn.config(text="Parar Reconhecimento")
            self.update_status("Reconhecimento ativo")
            self.add_to_log("🎯 Reconhecimento iniciado")
        else:
            self.is_recognizing = False
            self.recognize_btn.config(text="Iniciar Reconhecimento")
            self.update_status("Reconhecimento parado")
            self.add_to_log("⏹️ Reconhecimento parado")
            
    def capture_user(self):
        """Captura foto do usuário para cadastro"""
        name = self.name_entry.get().strip()
        user_id = self.id_entry.get().strip()
        
        if not name:
            messagebox.showerror("Erro", "Nome é obrigatório!")
            return
            
        if not user_id:
            user_id = name.lower().replace(" ", "_")
            
        if not self.current_frame is not None:
            messagebox.showerror("Erro", "Nenhum frame disponível da câmera!")
            return
            
        try:
            # Salvar imagem
            filename = f"faces/{user_id}.jpg"
            cv2.imwrite(filename, self.current_frame)
            
            # Validar e cadastrar usuário
            if self.face_detector.validate_captured_image(filename):
                self.user_manager.add_user(name, user_id)
                self.face_detector.load_known_faces()
                
                messagebox.showinfo("Sucesso", f"Usuário '{name}' cadastrado com sucesso!")
                self.name_entry.delete(0, tk.END)
                self.id_entry.delete(0, tk.END)
                self.refresh_users_list()
                self.add_to_log(f"👤 Usuário cadastrado: {name}")
            else:
                os.remove(filename)
                messagebox.showerror("Erro", "Nenhuma face detectada na imagem!")
                
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
            self.users_tree.insert("", tk.END, values=(user['name'], user['id'], user['registered_date']))
            
    def remove_selected_user(self):
        """Remove usuário selecionado"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um usuário para remover")
            return
            
        item = self.users_tree.item(selection[0])
        user_id = item['values'][1]
        user_name = item['values'][0]
        
        if messagebox.askyesno("Confirmar", f"Remover usuário '{user_name}'?"):
            try:
                self.user_manager.remove_user(user_id)
                self.face_detector.load_known_faces()
                self.refresh_users_list()
                messagebox.showinfo("Sucesso", f"Usuário '{user_name}' removido!")
                self.add_to_log(f"🗑️ Usuário removido: {user_name}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover usuário: {str(e)}")
                
    def generate_weekly_report(self):
        """Gera relatório semanal"""
        try:
            csv_file, pdf_file = self.report_generator.generate_weekly_report()
            messagebox.showinfo("Sucesso", f"Relatório gerado:\nCSV: {csv_file}\nPDF: {pdf_file}")
            self.add_to_log("📊 Relatório semanal gerado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")
            
    def generate_monthly_report(self):
        """Gera relatório mensal"""
        try:
            csv_file, pdf_file = self.report_generator.generate_monthly_report()
            messagebox.showinfo("Sucesso", f"Relatório gerado:\nCSV: {csv_file}\nPDF: {pdf_file}")
            self.add_to_log("📈 Relatório mensal gerado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")
            
    def add_to_log(self, message):
        """Adiciona mensagem ao log"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
    def update_status(self, message):
        """Atualiza barra de status"""
        self.status_var.set(message)

if __name__ == "__main__":
    root = tk.Tk()
    app = DetfaceDesktopApp(root)
    root.mainloop()