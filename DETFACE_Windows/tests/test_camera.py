#!/usr/bin/env python3
"""
Script de teste para verificar a performance da câmera
"""

import cv2
import time
import json

def test_camera_performance():
    """Testa a performance da câmera com as configurações otimizadas"""
    
    # Carregar configurações
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        camera_settings = config.get('camera_settings', {})
        fps = camera_settings.get('fps', 30)
        width = camera_settings.get('width', 640)
        height = camera_settings.get('height', 480)
        buffer_size = camera_settings.get('buffer_size', 1)
    except:
        fps = 30
        width = 640
        height = 480
        buffer_size = 1
    
    print(f"🎥 Testando câmera com configurações:")
    print(f"   FPS: {fps}")
    print(f"   Resolução: {width}x{height}")
    print(f"   Buffer: {buffer_size}")
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
    print()
    
    frame_count = 0
    start_time = time.time()
    last_fps_time = start_time
    
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
                print(f"📊 FPS atual: {fps_actual:.1f}")
                frame_count = 0
                start_time = current_time
                last_fps_time = current_time
            
            # Mostrar frame
            cv2.imshow('Teste de Câmera - DETFACE', frame)
            
            # Verificar tecla de saída
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Teste finalizado")
    
    return True

if __name__ == "__main__":
    test_camera_performance() 