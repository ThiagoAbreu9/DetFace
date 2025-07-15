#!/usr/bin/env python3
"""
Script de teste para verificar se o piscamento da câmera foi eliminado
"""

import cv2
import time
import json
import threading
from collections import deque

def test_smooth_camera():
    """Testa a câmera com configurações otimizadas para eliminar piscamento"""
    
    # Carregar configurações
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        camera_settings = config.get('camera_settings', {})
        fps = camera_settings.get('fps', 30)
        width = camera_settings.get('width', 640)
        height = camera_settings.get('height', 480)
        buffer_size = camera_settings.get('buffer_size', 1)
        processing_interval = config.get('performance', {}).get('processing_interval', 0.2)
    except:
        fps = 30
        width = 640
        height = 480
        buffer_size = 1
        processing_interval = 0.2
    
    print(f"🎥 Testando câmera SMOOTH com configurações:")
    print(f"   FPS: {fps}")
    print(f"   Resolução: {width}x{height}")
    print(f"   Buffer: {buffer_size}")
    print(f"   Intervalo de processamento: {processing_interval}s")
    print()
    
    # Tentar abrir câmera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Não foi possível abrir a câmera")
        return False
    
    # Configurar câmera
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
    
    print("✅ Câmera configurada com sucesso!")
    print("📺 Pressione 'q' para sair do teste")
    print("💡 Observe se há piscamento na imagem")
    print()
    
    # Variáveis para controle
    frame_count = 0
    start_time = time.time()
    last_fps_time = start_time
    last_processing_time = start_time
    
    # Simular processamento em thread separada
    def dummy_processing():
        nonlocal last_processing_time
        while True:
            current_time = time.time()
            if current_time - last_processing_time >= processing_interval:
                # Simular processamento pesado
                time.sleep(0.05)  # 50ms de processamento
                last_processing_time = current_time
            else:
                time.sleep(0.01)  # 10ms
    
    # Iniciar thread de processamento
    processing_thread = threading.Thread(target=dummy_processing, daemon=True)
    processing_thread.start()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Erro ao capturar frame")
                break
            
            frame_count += 1
            current_time = time.time()
            
            # Calcular FPS a cada segundo
            if current_time - last_fps_time >= 1.0:
                fps_actual = frame_count / (current_time - start_time)
                print(f"📊 FPS atual: {fps_actual:.1f} | Processamento: {processing_interval}s")
                frame_count = 0
                start_time = current_time
                last_fps_time = current_time
            
            # Adicionar texto informativo
            cv2.putText(frame, f"FPS: {fps_actual:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Processamento: {processing_interval}s", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Pressione 'q' para sair", (10, height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Mostrar frame
            cv2.imshow('Teste Câmera SMOOTH - DETFACE', frame)
            
            # Verificar tecla de saída
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Teste finalizado")
        print("💡 Se não houve piscamento, a otimização funcionou!")
    
    return True

if __name__ == "__main__":
    test_smooth_camera() 