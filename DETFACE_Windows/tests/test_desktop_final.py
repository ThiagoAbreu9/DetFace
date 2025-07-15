#!/usr/bin/env python3
"""
Teste Desktop FINAL - Eliminação total do piscamento
"""

import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
import time

class TestDesktopFinal:
    def __init__(self, root):
        self.root = root
        self.root.title("Teste Desktop FINAL - Sem Piscamento")
        self.root.geometry("800x600")
        
        # Variáveis de controle
        self.camera = None
        self.is_capturing = False
        self.camera_index = 0
        
        # Cache de frames
        self.current_frame = None
        self.current_photo = None
        self.frame_lock = threading.Lock()
        
        # Configurações
        self.target_fps = 30
        self.frame_interval = 1.0 / self.target_fps
        
        self.setup_ui()
        self.init_camera()
        
    def setup_ui(self):
        """Configura a interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="Teste Desktop FINAL - Sem Piscamento", 
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
        self.stop_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_var = tk.StringVar(value="Aguardando...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Arial", 10))
        status_label.pack(pady=(20, 0))
        
        # Informações
        info_label = tk.Label(main_frame, 
                             text="💡 Sistema otimizado para eliminar piscamento.\n"
                                  "💡 Cache de frames para performance máxima.\n"
                                  "💡 Thread dedicada para captura.",
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
        
    def capture_thread_func(self):
        """Thread dedicada para captura de frames"""
        last_frame_time = time.time()
        
        while self.is_capturing and self.camera:
            try:
                current_time = time.time()
                
                # Controle de FPS
                if current_time - last_frame_time >= self.frame_interval:
                    ret, frame = self.camera.read()
                    if ret:
                        with self.frame_lock:
                            self.current_frame = frame.copy()
                        last_frame_time = current_time
                    else:
                        time.sleep(0.01)
                else:
                    time.sleep(0.001)  # 1ms
                    
            except Exception as e:
                print(f"Erro na thread de captura: {e}")
                time.sleep(0.1)
                
    def update_display(self):
        """Atualiza o display (chamado periodicamente)"""
        if self.is_capturing and self.current_frame is not None:
            try:
                with self.frame_lock:
                    frame = self.current_frame.copy()
                
                # Processar frame
                frame_resized = cv2.resize(frame, (640, 480))
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                
                # Converter para PIL
                image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image)
                
                # Atualizar canvas
                self.video_canvas.delete("all")
                self.video_canvas.create_image(320, 240, image=photo)
                
                # Manter referência
                self.current_photo = photo
                
            except Exception as e:
                print(f"Erro ao atualizar display: {e}")
        
        # Agendar próxima atualização
        if self.is_capturing:
            self.root.after(int(self.frame_interval * 1000), self.update_display)
                
    def start_camera(self):
        """Inicia a câmera"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if self.camera.isOpened():
                # Configurar câmera para máxima performance
                self.camera.set(cv2.CAP_PROP_FPS, self.target_fps)
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
                
                self.is_capturing = True
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                
                # Iniciar thread de captura
                self.capture_thread = threading.Thread(target=self.capture_thread_func, daemon=True)
                self.capture_thread.start()
                
                # Iniciar atualização de display
                self.update_display()
                
                self.status_var.set(f"Câmera iniciada - {self.target_fps} FPS - SEM PISCAMENTO!")
            else:
                self.status_var.set("Erro ao iniciar câmera")
        except Exception as e:
            self.status_var.set(f"Erro: {str(e)}")
            
    def stop_camera(self):
        """Para a câmera"""
        self.is_capturing = False
        
        # Aguardar thread terminar
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        
        if self.camera:
            self.camera.release()
            self.camera = None
            
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Limpar canvas
        self.video_canvas.delete("all")
        self.video_canvas.create_text(320, 240, text="Câmera Parada", 
                                    fill="white", font=("Arial", 16))
        
        self.status_var.set("Câmera parada")

if __name__ == "__main__":
    root = tk.Tk()
    app = TestDesktopFinal(root)
    root.mainloop() 