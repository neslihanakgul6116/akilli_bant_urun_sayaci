import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("bant_takip.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sayimlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urun_sayisi INTEGER,
            zaman TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_to_db(count):
    init_db()
    conn = sqlite3.connect("bant_takip.db")
    cursor = conn.cursor()
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO sayimlar (urun_sayisi, zaman) VALUES (?, ?)", (count, zaman))
    conn.commit()
    conn.close()