import sqlite3

def crm_veritabanini_kur():
    # crm.db adında bir veritabanı dosyası oluşturur veya bağlanır
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()
    
    # 1. Müşteriler Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS musteriler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firma_adi TEXT NOT NULL,
        yetkili_kisi TEXT NOT NULL,
        eposta TEXT NOT NULL,
        telefon TEXT NOT NULL
    )
    """)
    
    # 2. Görevler (Task) Tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gorevler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        musteri_id INTEGER NOT NULL,
        gorev_basligi TEXT NOT NULL,
        sorumlu_kisi TEXT NOT NULL,
        durum TEXT NOT NULL DEFAULT 'Beklemede',
        oncelik TEXT NOT NULL,
        FOREIGN KEY (musteri_id) REFERENCES musteriler (id)
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crm_veritabanini_kur()
    print("CRM Veritabanı başarıyla kuruldu!")