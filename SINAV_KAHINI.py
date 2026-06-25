import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import requests
import json
import time

# Sayfa Ayarları ve Mobil Görünüm Optimizasyonu
st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

# --- MOBİL ARAYÜZ VE KARANLIK/AYDINLIK MOD STİL AYARLARI (CSS) ---
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
        color: #1E88E5 !important;
        margin-top: 10px;
        margin-bottom: 5px;
        border-bottom: 1px solid #ddd;
        padding-bottom: 2px;
    }
    /* Sohbet Kutuları ve Yazı Renkleri Sabitleme */
    .chat-box {
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        color: #111111 !important; 
        font-size: 14px;
        line-height: 1.4;
    }
    .chat-user { 
        background-color: #E3F2FD !important; 
        border-left: 5px solid #1E88E5 !important; 
    }
    .chat-kahin { 
        background-color: #FFF9C4 !important; 
        border-left: 5px solid #FBC02D !important; 
        font-style: italic; 
    }
    .chat-box b {
        color: #0D47A1 !important; 
    }
    .chat-kahin b {
        color: #F57F17 !important; 
    }
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

# --- GOOGLE SHEETS BAĞLANTISI ---
SHEET_ID = "1qjPw6aNw1PFREblbFCd8ZZ5LnlxnmBLbDMLuV5dMb1I"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzUKYurF1P5XA1fsgj4jOfWHzG1F9I8V3VmtZeJfAXLcdyZStX1PPsefg7XKQvz1CD1mg/exec"

# --- MESAJI BULUTA YAZMA FONKSİYONU ---
def buluta_mesaj_yaz(tarih, isim, mesaj):
    try:
        payload = {"tarih": tarih, "isim": isim, "mesaj": mesaj}
        requests.post(APPS_SCRIPT_URL, data=json.dumps(payload))
    except:
        pass

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
                if ders in st.session_state["secilen_dersler"]:
                    with st.expander(f"📁 {ders}", expanded=True):
                        for hafta, veri_listesi in sorted(haftalar.items()):
                            st.markdown(f"**🗓️ {hafta}. Hafta**")
                            for eleman in veri_listesi:
                                if eleman["tip"] == "metin":
                                    st.info(eleman['icerik'])
                                elif eleman["tip"] == "fotograf":
                                    st.image(eleman["icerik"], use_container_width=True)
        else:
            st.caption("Henüz yüklenmiş not yok.")

    with sekme2:
        st.subheader("📢 Ders Notu Yükle")
        with st.popover("➕ Dönem Derslerini Düzenle"):
            gecici_secimler = []
            for sinif_adi, ders_listesi in MÜFREDAT_HAVUZU.items():
                st.markdown(f"<div class='ders-baslik'>{sinif_adi}</div>", unsafe_allow_html=True)
                for ders in ders_listesi:
                    if st.checkbox(ders, value=(ders in st.session_state["secilen_dersler"]), key=f"pop_{ders}"):
                        gecici_secimler.append(ders)
            if st.button("Listeyi Güncelle", type="primary"):
                if gecici_secimler:
                    st.session_state["secilen_dersler"] = gecici_secimler
                    st.rerun()
        
        st.markdown("---")
        ders_adi = st.selectbox("Ders:", options=st.
