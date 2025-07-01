#!/usr/bin/env python3
"""
DETFACE - Interface Web para Câmera
Permite acesso à câmera através do navegador para ambientes web como Replit
"""

from flask import Flask, render_template, Response, request, jsonify
import cv2
import base64
import numpy as np
import threading
import time
import json
from face_detector import FaceDetector
from user_manager import UserManager

app = Flask(__name__)

class WebCamera:
    def __init__(self):
        self.face_detector = FaceDetector()
        self.user_manager = UserManager()
        self.camera = None
        self.is_capturing = False
        self.frame = None
        
    def init_camera(self):
        """Inicializa a câmera"""
        # Tentar diferentes índices de câmera
        for i in range(3):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        self.camera = cap
                        print(f"Câmera inicializada no índice {i}")
                        return True
                    cap.release()
            except:
                continue
        return False
    
    def start_capture(self):
        """Inicia captura de vídeo"""
        if not self.camera:
            if not self.init_camera():
                return False
        
        self.is_capturing = True
        threading.Thread(target=self._capture_loop, daemon=True).start()
        return True
    
    def _capture_loop(self):
        """Loop de captura de frames"""
        while self.is_capturing and self.camera:
            ret, frame = self.camera.read()
            if ret:
                self.frame = frame
            time.sleep(0.1)
    
    def stop_capture(self):
        """Para captura"""
        self.is_capturing = False
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def get_frame(self):
        """Retorna frame atual"""
        return self.frame
    
    def process_frame_data(self, frame_data):
        """Processa dados do frame enviados do navegador"""
        try:
            # Decodificar base64
            if ',' in frame_data:
                frame_data = frame_data.split(',')[1]
            
            img_data = base64.b64decode(frame_data)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return frame
        except Exception as e:
            print(f"Erro ao processar frame: {e}")
            return None

web_camera = WebCamera()

@app.route('/')
def index():
    """Página principal"""
    return render_template('camera.html')

@app.route('/api/capture_frame', methods=['POST'])
def capture_frame():
    """Captura frame para cadastro"""
    try:
        data = request.get_json()
        frame_data = data.get('frame')
        name = data.get('name')
        user_id = data.get('user_id')
        
        if not frame_data or not name:
            return jsonify({'success': False, 'error': 'Dados incompletos'})
        
        frame = web_camera.process_frame_data(frame_data)
        if frame is None:
            return jsonify({'success': False, 'error': 'Erro ao processar imagem'})
        
        # Salvar imagem
        filename = f"faces/{user_id}.jpg"
        cv2.imwrite(filename, frame)
        
        # Cadastrar usuário
        web_camera.user_manager.add_user(name, user_id)
        web_camera.face_detector.load_known_faces()
        
        return jsonify({'success': True, 'message': f'Usuário {name} cadastrado com sucesso!'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/recognize_frame', methods=['POST'])
def recognize_frame():
    """Reconhece faces no frame"""
    try:
        data = request.get_json()
        frame_data = data.get('frame')
        
        if not frame_data:
            return jsonify({'success': False, 'error': 'Frame não fornecido'})
        
        frame = web_camera.process_frame_data(frame_data)
        if frame is None:
            return jsonify({'success': False, 'error': 'Erro ao processar imagem'})
        
        # Detectar faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = web_camera.face_detector.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        results = []
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            features = web_camera.face_detector.extract_face_features(face_roi)
            
            if features is not None and len(web_camera.face_detector.known_face_features) > 0:
                from sklearn.metrics.pairwise import cosine_similarity
                similarities = []
                for known_features in web_camera.face_detector.known_face_features:
                    similarity = cosine_similarity([features], [known_features])[0][0]
                    similarities.append(similarity)
                
                best_match_idx = np.argmax(similarities)
                best_similarity = similarities[best_match_idx]
                
                if best_similarity > web_camera.face_detector.recognition_threshold:
                    name = web_camera.face_detector.known_face_names[best_match_idx]
                    user_id = web_camera.face_detector.known_face_ids[best_match_idx]
                    
                    # Registrar presença
                    web_camera.face_detector.register_attendance(user_id, name)
                    
                    results.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'name': name,
                        'confidence': float(best_similarity),
                        'recognized': True
                    })
                else:
                    results.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'name': 'Desconhecido',
                        'confidence': float(best_similarity),
                        'recognized': False
                    })
            else:
                results.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'name': 'Sem dados',
                    'confidence': 0.0,
                    'recognized': False
                })
        
        return jsonify({'success': True, 'faces': results})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/users')
def get_users():
    """Lista usuários cadastrados"""
    try:
        users = web_camera.user_manager.get_all_users()
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)