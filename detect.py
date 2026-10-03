from ultralytics import YOLO
import cv2

# YOLO modelini yükle
model = YOLO("models/yolov8n.pt")

def run_detection():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if ret:
        # YOLO ile nesne tespiti
        results = model(frame)
        count = len(results[0].boxes)
        return count
    else:
        raise RuntimeError("Kamera görüntüsü alınamadı.")