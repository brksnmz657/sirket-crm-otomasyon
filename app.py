import streamlit as st
import sqlite3
import pandas as pd
from crm_database import crm_veritabanini_kur

# Sayfa genişlik ve başlık ayarları
st.set_page_config(page_title="Kurumsal CRM Paneli", page_icon="📈", layout="wide")

# Veritabanını otomatik tetikle
crm_veritabanini_kur()

st.title("📈 Kurumsal CRM & Görev Takip Sistemi")
st.markdown("Müşteri ilişkileri yönetimi ve ekipler arası operasyonel iş takibi paneli.")
st.write("---")

# Veritabanından verileri DataFrame olarak çekme fonksiyonu
def crm_veri_yukle(tablo_adi):
    conn = sqlite3.connect("crm.db")
    df = pd.read_sql_query(f"SELECT * FROM {tablo_adi}", conn)
    conn.close()
    return df

musteriler_df = crm_veri_yukle("musteriler")
gorevler_df = crm_veri_yukle("gorevler")

# --- ARAYÜZ TASARIMI: İKİ SÜTUNLU YAPI ---
sol_col, sag_col = st.columns([1, 1.2])

with sol_col:
    st.subheader("👥 Yeni Müşteri Kaydı")
    with st.form("musteri_formu", clear_on_submit=True):
        firma = st.text_input("Firma Adı")
        yetkili = st.text_input("Yetkili Kişi (Ad Soyad)")
        eposta = st.text_input("E-posta")
        telefon = st.text_input("Telefon")
        musteri_submit = st.form_submit_button("Müşteriyi Kaydet")
        
        if musteri_submit and firma:
            conn = sqlite3.connect("crm.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO musteriler (firma_adi, yetkili_kisi, eposta, telefon)
                VALUES (?, ?, ?, ?)
            """, (firma, yetkili, eposta, telefon))
            conn.commit()
            conn.close()
            st.success(f"{firma} sisteme kaydedildi!")
            st.rerun()

    st.subheader("📋 Kayıtlı Firmalar")
    st.dataframe(musteriler_df, use_container_width=True, hide_index=True)

with sag_col:
    st.subheader("🎯 Yeni Görev / İş Atama")
    if not musteriler_df.empty:
        with st.form("gorev_formu", clear_on_submit=True):
            musteri_secim = st.selectbox(
                "İlgili Müşteri Firma:", 
                options=musteriler_df["id"].values,
                format_func=lambda x: musteriler_df[musteriler_df["id"] == x]["firma_adi"].values[0]
            )
            baslik = st.text_input("Görev Nedir? (Örn: Sözleşme imzalanacak)")
            sorumlu = st.text_input("Görevin Sorumlusu (Örn: Burak Sönmez)")
            oncelik = st.selectbox("Öncelik Seviyesi", ["Düşük", "Orta", "Yüksek"])
            gorev_submit = st.form_submit_button("Görevi Tanımla")
            
            if gorev_submit and baslik:
                conn = sqlite3.connect("crm.db")
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO gorevler (musteri_id, gorev_basligi, sorumlu_kisi, oncelik, durum)
                    VALUES (?, ?, ?, ?, 'Beklemede')
                """, (int(musteri_secim), baslik, sorumlu, oncelik))
                conn.commit()
                conn.close()
                st.success("Görev başarıyla oluşturuldu!")
                st.rerun()
    else:
        st.info("Görev atayabilmek için önce müşteri eklemelisiniz.")

# --- ALT KISIM: GÖREV TAKİP VE GÜNCELLEME TABLOSU ---
st.write("---")
st.subheader("📊 Aktif Görevlerin Operasyon Durumu")

if not gorevler_df.empty:
    id_firma_map = dict(zip(musteriler_df["id"], musteriler_df["firma_adi"]))
    gorevler_df["Firma Adı"] = gorevler_df["musteri_id"].map(id_firma_map)
    
    st.dataframe(
        gorevler_df[["id", "Firma Adı", "gorev_basligi", "sorumlu_kisi", "oncelik", "durum"]],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("#### ⚡ Hızlı Durum Güncelleme")
    g_col1, g_col2, g_col3 = st.columns(3)
    
    with g_col1:
        secilen_gorev_id = st.selectbox("Güncellenecek Görev ID:", options=gorevler_df["id"].values)
    with g_col2:
        yeni_durum = st.selectbox("Yeni Durum:", ["Beklemede", "Devam Ediyor", "Tamamlandı"])
    with g_col3:
        st.write("")
        st.write("")
        if st.button("🔄 Durumu Güncelle", use_container_width=True):
            conn = sqlite3.connect("crm.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE gorevler SET durum = ? WHERE id = ?", (yeni_durum, int(secilen_gorev_id)))
            conn.commit()
            conn.close()
            st.success("Görev durumu güncellendi!")
            st.rerun()
else:
    st.info("Sistemde henüz bir görev bulunmuyor.")
# --- VERİ SİLME BÖLÜMÜ ---
st.write("---")
st.subheader("🗑️ Hatalı Veri Silme Yönetimi")

sil_col1, sil_col2 = st.columns(2)

with sil_col1:
    st.markdown("#### ❌ Görev Sil")
    if not gorevler_df.empty:
        silinecek_gorev_id = st.selectbox("Silinecek Görev ID:", options=gorevler_df["id"].values, key="sil_g_id")
        g_detay = gorevler_df[gorevler_df["id"] == silinecek_gorev_id].iloc[0]
        st.caption(f"Silinecek İş: {g_detay['gorev_basligi']} ({g_detay['sorumlu_kisi']})")
        
        if st.button("🗑️ Görevi Sil", type="primary", key="btn_g_sil"):
            conn = sqlite3.connect("crm.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gorevler WHERE id = ?", (int(silinecek_gorev_id),))
            conn.commit()
            conn.close()
            st.success("Görev başarıyla silindi!")
            st.rerun()
    else:
        st.info("Silinecek görev yok.")

with sil_col2:
    st.markdown("#### ❌ Müşteri / Firma Sil")
    if not musteriler_df.empty:
        silinecek_m_id = st.selectbox("Silinecek Firma ID:", options=musteriler_df["id"].values, key="sil_m_id")
        m_detay = musteriler_df[musteriler_df["id"] == silinecek_m_id].iloc[0]
        st.caption(f"Silinecek Firma: {m_detay['firma_adi']}")
        
        if st.button("🗑️ Firmayı Sil", type="primary", key="btn_m_sil"):
            conn = sqlite3.connect("crm.db")
            cursor = conn.cursor()
            # Önce müşteriyi siliyoruz
            cursor.execute("DELETE FROM musteriler WHERE id = ?", (int(silinecek_m_id),))
            # İlişkisel bütünlük için o müşteriye bağlı görevleri de temizliyoruz
            cursor.execute("DELETE FROM gorevler WHERE musteri_id = ?", (int(silinecek_m_id),))
            conn.commit()
            conn.close()
            st.success("Firma ve firmaya bağlı tüm görevler silindi!")
            st.rerun()
    else:
        st.info("Silinecek firma yok.")
# --- FOOTER (KİŞİSEL BİLGİLER VE İLETİŞİM) ---
st.write("---")
st.markdown(
    """
    <style>
    .footer {
        text-align: center;
        color: #777777;
        padding: 10px;
        line-height: 1.6;
    }
    .footer a {
        color: #ff4b4b;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    </style>
    <div class="footer">
        <p><b>Geliştirici:</b> Burak Sönmez</p>
        <p>🎓 ESOGÜ - Siyaset Bilimi ve Kamu Yönetimi &nbsp;|&nbsp; 🎓 AÖF - Yönetim Bilişim Sistemleri</p>
        <p>📩 <a href="mailto:sonmezburak2007@gmail.com">sonmezburak2007@gmail.com</a> &nbsp;|&nbsp; 💼 <a href="https://www.linkedin.com/in/buraksönmez" target="_blank">LinkedIn Profilim</a></p>
    </div>
    """,
    unsafe_allow_html=True
)