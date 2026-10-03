import streamlit as st
import cv2
from ultralytics import YOLO
import sqlite3
import pandas as pd
from datetime import datetime
import torch
import time
import io
import winsound

st.set_page_config(
    page_title="Endüstriyel Çoklu Hat & Şişe Sayım Sistemi", 
    page_icon="🏭", 
    layout="wide"
)

# Model ve Donanım Optimizasyonu
@st.cache_resource
def load_model():
    model = YOLO("models/yolov8n.pt")
    if torch.cuda.is_available():
        model.to('cuda')
    return model

model = load_model()

# Veritabanı Altyapısı
def init_db():
    conn = sqlite3.connect("bant_takip.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sayimlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            urun_sayisi INTEGER, 
            hat_adi TEXT,
            vardiya TEXT,
            zaman TEXT
        )
    """)
    try:
        cursor.execute("ALTER TABLE sayimlar ADD COLUMN hat_adi TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE sayimlar ADD COLUMN vardiya TEXT")
    except:
        pass
    conn.commit()
    conn.close()

init_db()

# --- 🎯 ANA BAŞLIK VE SEKMELER ---
st.title("🏭 Fabrika Geneli - Çoklu Konveyör Hat ve Otomasyon Paneli")
st.markdown("---")

tab_hat1, tab_hat2, tab_rapor = st.tabs([
    "🟢 Hat 1: Şişe Giriş Bandı", 
    "🔵 Hat 2: Dolum & Paketleme Hattı", 
    "📊 Genel Raporlar & Yönetim"
])

# Ortak Vardiya Seçimi (Kenar Çubuğu)
st.sidebar.header("⚙️ Fabrika Genel Ayarları")
secilen_vardiya = st.sidebar.selectbox(
    "Aktif Çalışma Vardiyası", 
    ["Sabah Vardiyası (08:00 - 16:00)", "Akşam Vardiyası (16:00 - 00:00)", "Gece Vardiyası (00:00 - 08:00)"]
)
downtime_limit = st.sidebar.slider("Duruş Alarm Eşiği (Saniye)", min_value=5, max_value=60, value=15)


# --- HAT 1 İŞLEMLERİ ---
with tab_hat1:
    st.subheader("📺 Hat 1 Canlı Kamera Akışı (Giriş Hattı)")
    run_hat1 = st.checkbox("🔴 Hat 1 Akışını Başlat", key="h1")
    
    h1_col1, h1_col2 = st.columns([2, 1])
    with h1_col1:
        vid_ph1 = st.empty()
        alarm_ph1 = st.empty()
    with h1_col2:
        metric_ph1 = st.empty()
        st.markdown("---")
        table_ph1 = st.empty()

    if run_hat1:
        cap1 = cv2.VideoCapture(0)
        cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        count1 = 0
        ids1 = set()
        pos1 = {}
        last_count_time = time.time()
        has_counted_once = False

        while run_hat1:
            ret, frame = cap1.read()
            if not ret:
                break
            h, w, _ = frame.shape
            line_y = int(h * 0.5)
            
            results = model.track(frame, persist=True, conf=0.25, classes=[39], imgsz=320, verbose=False)
            boxes = results[0].boxes
            
            if boxes.id is not None:
                track_ids = boxes.id.int().cpu().tolist()
                xyxys = boxes.xyxy.cpu().numpy()
                for track_id, xyxy in zip(track_ids, xyxys):
                    x1, y1, x2, y2 = map(int, xyxy)
                    center_y = int((y1 + y2) / 2)
                    if track_id in pos1:
                        prev_y = pos1[track_id]
                        if (prev_y < line_y and center_y >= line_y) or (prev_y > line_y and center_y <= line_y):
                            if track_id not in ids1:
                                count1 += 1
                                ids1.add(track_id)
                                last_count_time = time.time()
                                has_counted_once = True
                                
                                conn = sqlite3.connect("bant_takip.db")
                                cur = conn.cursor()
                                cur.execute("INSERT INTO sayimlar (urun_sayisi, hat_adi, vardiya, zaman) VALUES (?, ?, ?, ?)", 
                                            (count1, "Hat 1 (Giriş)", secilen_vardiya, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                                conn.commit()
                                conn.close()
                    pos1[track_id] = center_y

            if not has_counted_once:
                alarm_ph1.info("ℹ️ Hat 1 Hazır: İlk ürünün çizgiyi kesmesi bekleniyor...")
            else:
                elapsed_time = time.time() - last_count_time
                if elapsed_time > downtime_limit:
                    alarm_ph1.error(f"⚠️ Hat 1 Durmuş Olabilir: {int(elapsed_time)} saniyedir ürün geçmiyor!")
                    try:
                        winsound.Beep(1000, 400) # Sesli uyarı
                    except:
                        pass
                else:
                    alarm_ph1.success("✅ Hat 1 Akışı Normal")

            cv2.line(frame, (0, line_y), (w, line_y), (0, 0, 255), 2)
            cv2.putText(frame, "HAT 1 SAYIM CIZGISI", (20, line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            res_frame = cv2.cvtColor(results[0].plot(img=frame), cv2.COLOR_BGR2RGB)
            vid_ph1.image(res_frame, channels="RGB", width='stretch')
            metric_ph1.metric(label="Hat 1 Toplam Sayım", value=f"{count1} Adet")
            
            try:
                conn = sqlite3.connect("bant_takip.db")
                df_h1 = pd.read_sql("SELECT urun_sayisi, zaman FROM sayimlar WHERE hat_adi='Hat 1 (Giriş)' ORDER BY id DESC LIMIT 5", conn)
                conn.close()
                table_ph1.dataframe(df_h1, width='stretch')
            except:
                pass
        cap1.release()
    else:
        vid_ph1.info("Hat 1 akışını başlatmak için kutucuğu işaretleyin.")


# --- HAT 2 İŞLEMLERİ ---
with tab_hat2:
    st.subheader("📺 Hat 2 Canlı Kamera Akışı (Dolum & Paketleme)")
    run_hat2 = st.checkbox("🔴 Hat 2 Akışını Başlat", key="h2")
    
    h2_col1, h2_col2 = st.columns([2, 1])
    with h2_col1:
        vid_ph2 = st.empty()
        alarm_ph2 = st.empty()
    with h2_col2:
        metric_ph2 = st.empty()
        st.markdown("---")
        table_ph2 = st.empty()

    if run_hat2:
        cap2 = cv2.VideoCapture(0) 
        cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        count2 = 0
        ids2 = set()
        pos2 = {}
        last_count_time2 = time.time()
        has_counted_once2 = False

        while run_hat2:
            ret, frame = cap2.read()
            if not ret:
                break
            h, w, _ = frame.shape
            line_y = int(h * 0.5)
            
            results = model.track(frame, persist=True, conf=0.25, classes=[39], imgsz=320, verbose=False)
            boxes = results[0].boxes
            
            if boxes.id is not None:
                track_ids = boxes.id.int().cpu().tolist()
                xyxys = boxes.xyxy.cpu().numpy()
                for track_id, xyxy in zip(track_ids, xyxys):
                    x1, y1, x2, y2 = map(int, xyxy)
                    center_y = int((y1 + y2) / 2)
                    if track_id in pos2:
                        prev_y = pos2[track_id]
                        if (prev_y < line_y and center_y >= line_y) or (prev_y > line_y and center_y <= line_y):
                            if track_id not in ids2:
                                count2 += 1
                                ids2.add(track_id)
                                last_count_time2 = time.time()
                                has_counted_once2 = True
                                
                                conn = sqlite3.connect("bant_takip.db")
                                cur = conn.cursor()
                                cur.execute("INSERT INTO sayimlar (urun_sayisi, hat_adi, vardiya, zaman) VALUES (?, ?, ?, ?)", 
                                            (count2, "Hat 2 (Dolum)", secilen_vardiya, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                                conn.commit()
                                conn.close()
                    pos2[track_id] = center_y

            if not has_counted_once2:
                alarm_ph2.info("ℹ️ Hat 2 Hazır: İlk ürünün çizgiyi kesmesi bekleniyor...")
            else:
                elapsed_time2 = time.time() - last_count_time2
                if elapsed_time2 > downtime_limit:
                    alarm_ph2.error(f"⚠️ Hat 2 Durmuş Olabilir: {int(elapsed_time2)} saniyedir ürün geçmiyor!")
                    try:
                        winsound.Beep(1200, 400) # Sesli uyarı
                    except:
                        pass
                else:
                    alarm_ph2.success("✅ Hat 2 Akışı Normal")

            cv2.line(frame, (0, line_y), (w, line_y), (255, 0, 0), 2)
            cv2.putText(frame, "HAT 2 SAYIM CIZGISI", (20, line_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            res_frame = cv2.cvtColor(results[0].plot(img=frame), cv2.COLOR_BGR2RGB)
            vid_ph2.image(res_frame, channels="RGB", width='stretch')
            metric_ph2.metric(label="Hat 2 Toplam Sayım", value=f"{count2} Adet")
            
            try:
                conn = sqlite3.connect("bant_takip.db")
                df_h2 = pd.read_sql("SELECT urun_sayisi, zaman FROM sayimlar WHERE hat_adi='Hat 2 (Dolum)' ORDER BY id DESC LIMIT 5", conn)
                conn.close()
                table_ph2.dataframe(df_h2, width='stretch')
            except:
                pass
        cap2.release()
    else:
        vid_ph2.info("Hat 2 akışını başlatmak için kutucuğu işaretleyin.")


# --- GENEL RAPORLAR VE YÖNETİM ---
with tab_rapor:
    st.subheader("📈 Fabrika Geneli Üretim Raporları ve Analiz")
    
    try:
        conn = sqlite3.connect("bant_takip.db")
        df_all = pd.read_sql("SELECT * FROM sayimlar ORDER BY id DESC", conn)
        conn.close()
        
        if not df_all.empty:
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                secilen_hat_filtre = st.selectbox("Hata Göre Filtrele", ["Tümü"] + list(df_all["hat_adi"].dropna().unique()))
            with r_col2:
                secilen_vardiya_filtre = st.selectbox("Vardiyaya Göre Filtrele", ["Tümü"] + list(df_all["vardiya"].dropna().unique()))
            
            df_filtered = df_all.copy()
            if secilen_hat_filtre != "Tümü":
                df_filtered = df_filtered[df_filtered["hat_adi"] == secilen_hat_filtre]
            if secilen_vardiya_filtre != "Tümü":
                df_filtered = df_filtered[df_filtered["vardiya"] == secilen_vardiya_filtre]
                
            st.dataframe(df_filtered, width='stretch')
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_filtered.to_excel(writer, index=False, sheet_name='Fabrika_Raporu')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 Tüm Fabrika Raporunu Excel Olarak İndir (.xlsx)",
                data=processed_data,
                file_name=f"fabrika_genel_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("---")
            st.subheader("🔐 Yönetici Güvenlik Alanı")
            admin_sifre = st.text_input("Veritabanını sıfırlamak için yönetici şifresini girin:", type="password", key="adm_pass")
            if admin_sifre == "admin123":
                if st.button("🗑️ Tüm Fabrika Veritabanını Temizle"):
                    conn = sqlite3.connect("bant_takip.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM sayimlar")
                    conn.commit()
                    conn.close()
                    st.success("Fabrika veritabanı başarıyla sıfırlandı!")
                    st.rerun()
            elif admin_sifre != "":
                st.error("Hatalı şifre!")
        else:
            st.info("Henüz kayıtlı fabrika verisi bulunmuyor.")
    except Exception as e:
        st.error(f"Rapor yüklenirken hata oluştu: {e}")