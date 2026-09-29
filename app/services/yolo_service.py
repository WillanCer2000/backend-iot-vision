from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np

# Obtener la ruta absoluta del archivo best.pt dentro de la carpeta app
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "best.pt"

# Cargar el modelo con los pesos de Arzuza
model = YOLO(str(MODEL_PATH))

def analizar_imagen_bytes(image_bytes: bytes):
    # Convertir bytes de la imagen recibida a formato OpenCV
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Ejecutar la inferencia con el modelo custom
    results = model(img)
    
    detections = []
    for box in results[0].boxes:
        detections.append({
            "class": model.names[int(box.cls[0])],
            "confidence": round(float(box.conf[0]), 2),
            "bbox": [round(x, 2) for x in box.xywh[0].tolist()]
        })
        
    return detections