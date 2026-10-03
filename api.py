from fastapi import FastAPI
from detect import run_detection
from utils import log_to_db  # log_count yerine log_to_db kullanıyoruz

app = FastAPI()

@app.get("/sayim")
def sayim():
    try:
        # Kameradan sayımı al ve SQLite veritabanına logla
        urun_sayisi = run_detection()
        log_to_db(urun_sayisi)
    except Exception as e:
        urun_sayisi = 0
        
    return {
        "durum": "Aktif",
        "toplam_urun_sayisi": urun_sayisi,
        "mesaj": "Ürün sayımı başarıyla gerçekleştirildi ve veritabanına kaydedildi."
    }