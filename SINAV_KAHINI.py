import streamlit as st
import google.generativeai as genai
from datetime import datetime
from pypdf import PdfReader
import io
import pandas as pd

# Sayfa Ayarları ve Mobil Görünüm Optimizasyonu
st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

# --- MOBİL ARAYÜZ STİL AYARLARI (CSS) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100% !important;
        border-radius: 12px !important;
        height: 45px !important;
        font-weight: bold !important;
    }
    .stTextArea textarea {
        border-radius: 10px !important;
    }
    button[data-baseweb="tab"] {
        font-size: 14px !important;
        padding: 10px 5px !important;
    }
    .ders-baslik {
        font-weight: bold;
        color: #1E88E5;
        margin-top: 10px;
        margin-bottom: 5px;
        border-bottom: 1px solid #ddd;
        padding-bottom: 2px;
    }
    .chat-box {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 8px;
    }
    .chat-user { background-color: #F0F2F6; border-left: 5px solid #1E88E5; }
    .chat-kahin { background-color: #FFF3CD; border-left: 5px solid #FFC107; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# --- SANAL HAFIZA KURULUMU ---
if "ders_notlari" not in st.session_state:
    st.session_state["ders_notlari"] = {}

if "api_key_kayitli" not in st.session_state:
    st.session_state["api_key_kayitli"] = ""

if "chat_isim" not in st.session_state:
    st.session_state["chat_isim"] = ""

# --- MÜFREDAT VERİTABANI ---
MÜFREDAT_HAVUZU = {
    "1. SINIF DERSLERİ": [
        "İktisada Giriş I", "Genel Hukuk", "Bilgisayar Kullanımı ve Ofis Uygulamaları", 
        "Genel İşletme", "Finansal Muhasebe I", "İktisada Giriş II", 
        "Yönetim ve Organizasyon", "Ticari Belgeler", "Ticari ve Mali Matematik", 
        "Finansal Muhasebe II", "Ticaret Hukuku"
    ],
    "2. SINIF DERSLERİ": [
        "Finansal Okuryazarlık", "Finans Matematiği", "Muhasebe Paket Programları I", 
        "Şirketler Muhasebesi", "Stratejik Yönetim", "Halkla İlişkiler", 
        "İş ve Sosyal Güvenlik Hukuku", "Muhasebe Meslek Mevzuatı ve Etiği", "E-Ticaret", 
        "Muhasebe Paket Programları II", "Para ve Sermaye Piyasası Kurumları", 
        "Finansal Tablolar Analizi", "İhtisas Muhasebesi", "Kıymetli Evrak Hukuku", 
        "Girişimcilik", "İletişim ve Etkili Sunum Teknikleri", "Davranışsal İktisat", 
        "Dış Ticaret İşlemleri", "Pazarlama Yönetimi"
    ],
    "3. SINIF DERSLERİ": [
        "Vergi Hukuku", "Yatırım Analizi ve Portföy Yönetimi", "Finansal Yönetim I", 
        "Maliyet Muhasebesi I", "Sermaye Piyasası Mevzuatı", "Türkiye Ekonomisi", 
        "Borsa İşlemleri", "Muhasebede Seçilmiş Konular ve Örnek Olaylar", "İstatistik", 
        "Enflasyon Muhasebesi", "Finansal Sistem ve Uygulamaları I", "Finansal Yönetim II", 
        "Maliyet Muhasebesi II", "Türk Vergi Sistemi ve Uygulamaları", "Muhasebe Denetimi", 
        "Yatırım Kuruluşları ve Araçları", "Yönlendirilmiş Çalışmalar", "Davranış Bilimleri", 
        "Dış Ticaret İşlemleri Muhasebesi", "Sosyoloji"
    ],
    "4. SINIF DERSLERİ": [
        "Muhasebe Standartları", "Finansal Sistem ve Uygulamaları II", "Maliyet Yönetimi", 
        "Davranışsal Finans", "Yönetim Muhasebesi", "Bilimsel Araştırma Yöntemleri", 
        "Türev Piyasalar ve Risk Yönetimi", "Muhasebe Bilgi Sistemleri", "Kobi Finansmanı", 
        "İş Sağlığı ve Güvenliği", "İnsan Kaynakları Yönetimi", "İşletmede Mesleki Eğitim"
    ]
}

if "secilen_dersler" not in st.session_state:
    st.session_state["secilen_dersler"] = ["Finansal Muhasebe I", "Finansal Muhasebe II", "Ticaret Hukuku"]

HESAP_PLANI = {"100": "KASA", "101": "ALINAN ÇEKLER", "102": "BANKALAR", "103": "VERİLEN ÇEKLER (-)", "120": "ALICILAR", "121": "ALACAK SENETLERİ", "153": "TİCARİ MALLAR", "191": "İNDİRİLECEK KDV", "254": "TAŞITLAR", "255": "DEMİRBAŞLAR", "257": "BİRİKMİŞ AMORTİSMANLAR (-)", "320": "SATICILAR", "321": "BORÇ SENETLERİ", "391": "HESAPLANAN KDV", "500": "SERMAYE", "600": "YURTİÇİ SATIŞLAR", "621": "STMM (-)", "770": "GENEL YÖNETİM GİDERLERİ"}

# --- GOOGLE SHEETS VERİTABANI BAĞLANTI AYARI ---
SHEET_ID = "1qjPw6aNw1PFREblbFCd8ZZ5LnlxnmBLbDMLuV5dMb1I"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# --- GİRİŞ KONTROLÜ ---
if not st.session_state["api_key_kayitli"]:
    st.title("🔮 Sınav Kahini Giriş")
    st.subheader("Hoş geldiniz")
    girilen_key = st.text_input("🔑 Gemini API Key Girin:", type="password")
    if st.button("Sisteme Giriş Yap 🚀", use_container_width=True):
        if girilen_key:
            st.session_state["api_key_kayitli"] = girilen_key
            st.rerun()
else:
    genai.configure(api_key=st.session_state["api_key_kayitli"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    st.title("🔮 Sınav Kahini")
    if st.button("🔒 Oturumu Kapat", use_container_width=True):
        st.session_state["api_key_kayitli"] = ""
        st.rerun()

    st.markdown("---")

    # --- 5 SEKME SİSTEMİ ---
    sekme1, sekme2, sekme3, sekme4, sekme5 = st.tabs(["📁 Arşiv", "📢 Not Yükle", "📝 Soru Odası", "📊 Hesapla", "💬 Bölüm Chat"])

    with sekme1:
        st.subheader("📌 Ders Kütüphanesi")
        if st.session_state["ders_notlari"]:
            for ders, haftalar in st.session_state["ders_notlari"].items():
