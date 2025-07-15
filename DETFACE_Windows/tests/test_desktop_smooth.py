#!/usr/bin/env python3
"""
Teste Desktop SMOOTH - Sem bounding box para eliminar piscamento
"""

import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
import time
from collections import deque

class TestDesktopSmooth:
    def __init__(self, root):
        self.root = root
        self.root.title("Teste Desktop SMOOTH - Sem Bounding Box")
        self.root.geometry("800x600")
        
        # Variáveis de controle
        self.camera = None
        self.is_capturing = False
        self.is_recognizing = False
        self.camera_index = 0
        self.photo_reference = None
        
        # Variáveis para thread de processamento
        self.processing_thread = None
        self.stop_processing = False
        self.frame_queue = deque(maxlen=3)
        self.processing_lock = threading.Lock()
        
        # Variáveis para overlay
        self.recognition_timer = None
        
        self.setup_ui()
        self.init_camera()
        
    def setup_ui(self):
        """Configura a interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="Teste Desktop SMOOTH - Sem Bounding Box", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Canvas para vídeo
        self.video_canvas = tk.Canvas(main_frame, width=640, height=480, bg="black")
        self.video_canvas.pack(pady=(0, 20))
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        self.start_btn = ttk.Button(button_frame, text="📹 Iniciar Câmera", 
                                   command=self.start_camera)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Parar Câmera", 
                                  command=self.stop_camera, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.recognize_btn = ttk.Button(button_frame, text="🎯 Iniciar Reconhecimento", 
                                       command=self.toggle_recognition, state=tk.DISABLED)
        self.recognize_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_var = tk.StringVar(value="Aguardando...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Arial", 10))
        status_label.pack(pady=(20, 0))
        
        # Informações
        info_label = tk.Label(main_frame, 
                             text="💡 A câmera deve funcionar sem piscamento.\n"
                                  "💡 O reconhecimento aparece como overlay de texto.",
                             font=("Arial", 10), fg="blue", justify=tk.LEFT)
        info_label.pack(pady=(10, 0))
        
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
                        self.status_var.set(f"Câmera encontrada no índice {i}")
                        self.start_btn.config(state=tk.NORMAL)
                        return True
                    cap.release()
            except:
                continue
        
        self.status_var.set("Nenhuma câmera encontrada")
        return False
        
    def process_frames_thread(self):
        """Thread separada para processar frames (sem bounding box)"""
        last_processing_time = time.time()
        processing_interval = 0.5  # 500ms entre processamentos
        face_count = 0
        
        while not self.stop_processing:
            try:
                if len(self.frame_queue) == 0:
                    time.sleep(0.01)
                    continue
                
                current_time = time.time()
                
                if current_time - last_processing_time >= processing_interval:
                    frame = self.frame_queue[-1]
                    
                    # Simular detecção de faces (sem desenhar)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(gray, 1.2, 5)
                    
                    if len(faces) > 0:
                        face_count += 1
                        # Mostrar overlay apenas quando detectar faces
                        overlay_message = f"👤 {len(faces)} face(s) detectada(s) - #{face_count}"
                        self.root.after(0, lambda: self.show_recognition_overlay(overlay_message, 2))
                    
                    last_processing_time = current_time
                else:
                    time.sleep(0.01)
                    
            except Exception as e:
                print(f"Erro na thread: {e}")
                time.sleep(0.1)
                
    def show_recognition_overlay(self, message, duration=2):
        """Mostra overlay de reconhecimento"""
        # Cancelar timer anterior
        if self.recognition_timer:
            self.root.after_cancel(self.recognition_timer)
        
        # Limpar overlay anterior
        self.video_canvas.delete("overlay")
        
        # Criar novo overlay
        self.video_canvas.create_text(
            320, 50,
            text=message,
            fill="lime",
            font=("Arial", 14, "bold"),
            tags="overlay"
        )
        
        # Configurar timer para remover
        self.recognition_timer = self.root.after(duration * 1000, self.clear_overlay)
    
    def clear_overlay(self):
        """Remove overlay"""
        self.video_canvas.delete("overlay")
        self.recognition_timer = None
                
    def start_camera(self):
        """Inicia a câmera"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if self.camera.isOpened():
                # Configurar câmera
                self.camera.set(cv2.CAP_PROP_FPS, 30)
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
                
                self.is_capturing = True
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                self.recognize_btn.config(state=tk.NORMAL)
                
                # Iniciar thread de captura
                self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
                self.capture_thread.start()
                
                self.status_var.set("Câmera iniciada - Sem piscamento!")
            else:
                self.status_var.set("Erro ao iniciar câmera")
        except Exception as e:
            self.status_var.set(f"Erro: {str(e)}")
            
    def stop_camera(self):
        """Para a câmera"""
        self.is_capturing = False
        self.is_recognizing = False
        
        # Parar thread de processamento
        self.stop_processing = True
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)
        
        if self.camera:
            self.camera.release()
            self.camera = None
            
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.recognize_btn.config(state=tk.DISABLED, text="🎯 Iniciar Reconhecimento")
        
        # Limpar canvas
        self.video_canvas.delete("all")
        self.video_canvas.create_text(320, 240, text="Câmera Parada", 
                                    fill="white", font=("Arial", 16))
        
        self.status_var.set("Câmera parada")
        
    def capture_loop(self):
        """Loop de captura - SEMPRE frame limpo"""
        while self.is_capturing and self.camera:
            ret, frame = self.camera.read()
            if ret:
                # Adicionar frame à fila apenas se reconhecimento ativo
                if self.is_recognizing:
                    self.frame_queue.append(frame.copy())
                
                # SEMPRE exibir frame limpo (sem bounding box)
                self.display_frame_on_canvas(frame)
                
            time.sleep(0.03)  # ~30 FPS
            
    def display_frame_on_canvas(self, frame):
        """Exibe frame no canvas"""
        try:
            frame_resized = cv2.resize(frame, (640, 480))
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            self.video_canvas.delete("all")
            self.video_canvas.create_image(320, 240, image=photo)
            
            self.photo_reference = photo
            
        except Exception as e:
            print(f"Erro ao exibir frame: {e}")
            
    def toggle_recognition(self):
        """Liga/desliga reconhecimento"""
        if not self.is_recognizing:
            self.is_recognizing = True
            self.recognize_btn.config(text="⏹️ Parar Reconhecimento")
            self.status_var.set("Reconhecimento ativo - Processamento em background")
            
            # Iniciar thread de processamento
            self.stop_processing = False
            self.processing_thread = threading.Thread(target=self.process_frames_thread, daemon=True)
            self.processing_thread.start()
        else:
            self.is_recognizing = False
            self.recognize_btn.config(text="🎯 Iniciar Reconhecimento")
            self.status_var.set("Reconhecimento parado")
            
            # Parar thread de processamento
            self.stop_processing = True
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=1.0)

if __name__ == "__main__":
    root = tk.Tk()
    app = TestDesktopSmooth(root)
    root.mainloop() 