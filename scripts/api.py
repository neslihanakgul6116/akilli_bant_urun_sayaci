from fastapi import FastAPI

app = FastAPI()

@app.get("/sayim")
def sayim():
    # Burada gerçek sayım sonucunu detect.py’den alabilirsin
    return {"mesaj": "Ürün sayacı çalışıyor"}
