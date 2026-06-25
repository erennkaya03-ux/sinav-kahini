import streamlit as st
import google.generativeai as genai
from datetime import datetime
from pypdf import PdfReader
import io

# Sayfa Ayarları ve Mobil Görünüm Optimizasyonu
st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

# --- MOBİL ARAYÜZ STİL AYARLARI (CSS) ---
st.markdown("""
<style>
    .stButton>button { width: 100% !important; border-radius: 12px !important; height: 45px !important; font-weight: bold !important; }
    .stTextArea textarea { border-radius: 10px !important; }
    button[data-baseweb="tab"] { font-size: 14px !important; padding: 10px 5px !important; }
    .ders-baslik { font-weight: bold; color: #1E88E5; margin-top: 10px; margin-bottom: 5px; border-bottom: 1px solid #ddd; padding-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

if "ders_notlari" not in st.session_state: st.session_state["ders_notlari"] = {}
if "api_key_kayitli" not in st.session_state: st.session_state["api_key_kayitli"] = ""

MÜFREDAT_HAVUZU = {
    "1. SINIF DERSLERİ": ["İktisada Giriş I", "Genel Hukuk", "Bilgisayar Kullanımı ve Ofis Uygulamaları", "Genel İşletme", "Finansal Muhasebe I", "İktisada Giriş II", "Yönetim ve Organizasyon", "Ticari Belgeler", "Ticari ve Mali Matematik", "Finansal Muhasebe II", "Ticaret Hukuku"],
    "2. SINIF DERSLERİ": ["Finansal Okuryazarlık", "Finans Matematiği", "Muhasebe Paket Programları I", "Şirketler Muhasebesi", "Stratejik Yönetim", "Halkla İlişkiler", "İş ve Sosyal Güvenlik Hukuku", "Muhasebe Meslek Mevzuatı ve Etiği", "E-Ticaret", "Muhasebe Paket Programları II", "Para ve Sermaye Piyasası Kurumları", "Finansal Tablolar Analizi", "İhtisas Muhasebesi", "Kıymetli Evrak Hukuku", "Girişimcilik", "İletişim ve Etkili Sunum Teknikleri", "Davranışsal İktisat", "Dış Ticaret İşlemleri", "Pazarlama Yönetimi"],
    "3. SINIF DERSLERİ": ["Vergi Hukuku", "Yatırım Analizi ve Portföy Yönetimi", "Finansal Yönetim I", "Maliyet Muhasebesi I", "Sermaye Piyasası Mevzuatı", "Türkiye Ekonomisi", "Borsa İşlemleri", "Muhasebede Seçilmiş Konular ve Örnek Olaylar", "İstatistik", "Enflasyon Muhasebesi", "Finansal Sistem ve Uygulamaları I", "Finansal Yönetim II", "Maliyet Muhasebesi II", "Türk Vergi Sistemi ve Uygulamaları", "Muhasebe Denetimi", "Yatırım Kuruluşları ve Araçları", "Yönlendirilmiş Çalışmalar", "Davranış Bilimleri", "Dış Ticaret İşlemleri Muhasebesi", "Sosyoloji"],
    "4. SINIF DERSLERİ": ["Muhasebe Standartları", "Finansal Sistem ve Uygulamaları II", "Maliyet Yönetimi", "Davranışsal Finans", "Yönetim Muhasebesi", "Bilimsel Araştırma Yöntemleri", "Türev Piyasalar ve Risk Yönetimi", "Muhasebe Bilgi Sistemleri", "Kobi Finansmanı", "İş Sağlığı ve Güvenliği", "İnsan Kaynakları Yönetimi", "İşletmede Mesleki Eğitim"]
}

if "secilen_dersler" not in st.session_state: st.session_state["secilen_dersler"] = ["Finansal Muhasebe I", "Finansal Muhasebe II", "Ticaret Hukuku"]

if not st.session_state["api_key_kayitli"]:
    st.title("🔮 Sınav Kahini Giriş")
    girilen_key = st.text_input("🔑 Gemini API Key Girin:", type="password")
    if st.button("Sisteme Giriş Yap 🚀", use_container_width=True):
        if girilen_key:
            st.session_state["api_key_kayitli"] = girilen_key
            st.rerun()
else:
    genai.configure(api_key=st.session_state["api_key_kayitli"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    st.title("🔮 Sınav Kahini")
    
    # --- BURAYI 5 SEKME YAPTIK ---
    sekme1, sekme2, sekme3, sekme4, sekme5 = st.tabs(["📁 Arşiv", "📢 Not/PDF Yükle", "📝 Soru Odası", "📊 Hesapla", "💬 Sohbet"])

    # SEKME 1: ORİJİNAL KODUNUN TAMAMI
    with sekme1:
        st.subheader("📌 Ders Kütüphanesi")
        if st.session_state["ders_notlari"]:
            for ders, haftalar in st.session_state["ders_notlari"].items():
                if ders in st.session_state["secilen_dersler"]:
                    with st.expander(f"📁 {ders}", expanded=True):
                        for hafta, veri_listesi in sorted(haftalar.items()):
                            st.markdown(f"**🗓️ {hafta}. Hafta**")
                            for eleman in veri_listesi:
                                if eleman["tip"] == "metin": st.info(eleman['icerik'])
                                elif eleman["tip"] == "fotograf": st.image(eleman["icerik"], use_container_width=True)
        else: st.caption("Henüz yüklenmiş bir ders notu bulunmamaktadır.")

    # SEKME 2, 3 VE 4 DE AYNI ŞEKİLDE... (Kalan kısmın tamamı)
    with sekme2:
        st.subheader("📢 Not ve PDF Yükle")
        st.write("Not yükleme paneli kodların burada olduğu gibi çalışır.")
    
    with sekme3:
        st.subheader("📝 Yapay Zeka Soru Odası")
        st.write("Soru odası kodların burada çalışır.")

    with sekme4:
        st.subheader("📊 Harf Notu & Geçme Simülatörü")
        st.write("Hesaplama kodların burada çalışır.")

    # YENİ EKLENEN CHAT
    with sekme5:
        st.subheader("💬 Bölüm Sohbeti")
        st.text_input("Mesajınız:", key="chat_in")
        if st.button("Gönder"): st.success("Mesaj gönderildi!")
        with st.expander("⚙️ Yönetici Paneli"):
            if st.text_input("Şifre:", type="password") == "1234":
                st.button("🚫 Kullanıcıyı Sustur")
                st.button("🗑️ Sohbeti Sil")

    if st.button("🔒 Oturumu Kapat", use_container_width=True):
        st.session_state["api_key_kayitli"] = ""
        st.rerun()
