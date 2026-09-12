from ultralytics import YOLO
import cv2

# YOLO modelini yükle
model = YOLO("models/yolov8n.pt")

# Kameradan tek kare al
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()

if ret:
    # YOLO ile nesne tespiti
    results = model(frame)
    annotated = results[0].plot()

    # Ürün sayısını yazdır
    count = len(results[0].boxes)
    print("Bu karede ürün sayısı:", count)

    # Görüntüyü göster (sabit kalır)
    cv2.imshow("Akıllı Bant Ürün Sayacı - Tek Kare", annotated)
    cv2.waitKey(0)  # Bir tuşa basana kadar pencere açık kalır
    cv2.destroyAllWindows()
else:
    print("Kamera görüntüsü alınamadı.")
