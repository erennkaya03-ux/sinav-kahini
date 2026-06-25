import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import requests
import json
import time
import random

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

# --- GOOGLE SHEETS VE APPS SCRIPT BAĞLANTILARI ---
SHEETS_YENI_LINK = "https://script.google.com/macros/s/AKfycbzExJPw5JDjfzInJ3_sPwNfv5en7aIVsl29vMHCtQlLIJq1fgZmxZrDDi6Y4SaYw6XuQA/exec"
SHEET_ID = "1qjPw6aNw1PFREblbFCd8ZZ5LnlxnmBLbDMLuV5dMb1I"

anlik_zaman = int(time.time())
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&cache_bust={anlik_zaman}"

# --- MESAJI BULUTA YAZMA FONKSİYONU ---
def buluta_mesaj_yaz(tarih, isim, mesaj):
    try:
        payload = {"tarih": tarih, "isim": isim, "mesaj": mesaj}
        requests.post(SHEETS_YENI_LINK, data=json.dumps(payload))
    except:
        pass

# --- GİRİŞ PANELİ VE ANA UYGULAMA MANTIĞI ---
if st.session_state["api_key_kayitli"] == "":
    st.title("🔮 Sınav Kahini Giriş")
    st.subheader("Hoş geldiniz")
    girilen_key = st.text_input("🔑 Gemini API Key Girin:", type="password")
    if st.button("Sisteme Giriş Yap 🚀", use_container_width=True):
        if girilen_key:
            st.session_state["api_key_kayitli"] = girilen_key.strip()
            st.success("Giriş başarılı! Sayfa yükleniyor...")
            time.sleep(0.5)
            st.rerun()
else:
    # Yapay zekayı ayağa kaldırıyoruz
    try:
        genai.configure(api_key=st.session_state["api_key_kayitli"])
        model = genai.GenerativeModel('gemini-2.5-flash')
    except:
        st.error("API Anahtarı yapılandırılamadı. Lütfen geçerli bir anahtar girin.")
    
    st.title("🔮 Sınav Kahini")
    if st.button("🔒 Oturumu Kapat", use_container_width=True):
        st.session_state["api_key_kayitli"] = ""
        st.rerun()

    st.markdown("---")

    # --- 5 SEKME SİSTEMİ ---
    sekme1, sekme2, sekme3, sekme4, sekme5 = st.tabs(["📁 Arşiv", "📢 Not Yükle", "📝 Soru Odası", "📊 Hesapla", "💬 Bölüm Chat"])

    # SEKME 1: ARŞİV (YENİLENDİ - ARTIK DERSLER HEP GÖZÜKECEK)
    with sekme1:
        st.subheader("📌 Ders Kütüphanesi")
        # Seçilen dersleri dönüyoruz, hafıza boş olsa bile klasörler açılacak
        for ders in st.session_state["secilen_dersler"]:
            with st.expander(f"📁 {ders}", expanded=True):
                # Bu derse ait bir not girilmiş mi kontrol et
                if ders in st.session_state["ders_notlari"] and st.session_state["ders_notlari"][ders]:
                    for hafta, veri_listesi in sorted(st.session_state["ders_notlari"][ders].items()):
                        st.markdown(f"**🗓️ {hafta}. Hafta**")
                        for eleman in veri_listesi:
                            if eleman["tip"] == "metin":
                                st.info(eleman['icerik'])
                else:
                    st.caption("📥 Bu derse henüz bir ders notu yüklenmemiş. Not Yükle sekmesinden ekleme yapabilirsin kanka.")

    # SEKME 2: NOT YÜKLE
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
        ders_adi = st.selectbox("Ders:", options=st.session_state["secilen_dersler"])
        secilen_text_hafta = st.number_input("Hafta:", min_value=1, max_value=14, value=1)
        ham_not = st.text_area("📝 Not ekleyin:")
        if st.button("🚀 Gönder", use_container_width=True):
            if ders_adi not in st.session_state["ders_notlari"]:
                st.session_state["ders_notlari"][ders_adi] = {}
            if secilen_text_hafta not in st.session_state["ders_notlari"][ders_adi]:
                st.session_state["ders_notlari"][ders_adi][secilen_text_hafta] = []
            if ham_not:
                st.session_state["ders_notlari"][ders_adi][secilen_text_hafta].append({"tip": "metin", "icerik": ham_not})
            st.success("Arşive eklendi!")

    # SEKME 3: SORU ODASI
    with sekme3:
        st.subheader("📝 Yapay Zeka Soru Odası")
        ders_kontrol = st.selectbox("Ders Seçin:", options=st.session_state["secilen_dersler"], key="sb_ders")
        zorluk = st.select_slider("Zorluk:", options=["Kolay", "Orta", "Zor", "Hocanın Saplama Modu"])
        ornek_soru = st.text_area("✍️ Soru Yazın (Opsiyonel):")
        if st.button("🔮 Soruyu Çöz / Üret", use_container_width=True):
            if not ornek_soru:
                komut = f"{ders_kontrol} dersi için {zorluk} seviyesinde soru çöz/üret."
            else:
                komut = f"{ders_kontrol} sorusunu çöz: {ornek_soru}"
            st.session_state["mob_soru"] = model.generate_content(komut).text
        if "mob_soru" in st.session_state:
            st.markdown(st.session_state["mob_soru"])

    # SEKME 4: HESAPLA (ESKİ SİSTEM: HEDEFE GÖRE HESAPLAMA SİSTEMİ)
    with sekme4:
        st.subheader("📊 Harf Notu & Hedef Simülatörü")
        
        vize_notu = st.slider("Vize Notun Kaç?", 0, 100, 50)
        vize_orani = st.slider("Vize Yüzdesi (%)", 10, 90, 40)
        final_orani = 100 - vize_orani
        st.caption(f"Sistem Etkisi: %{vize_orani} Vize - %{final_orani} Final")
        
        st.markdown("---")
        st.markdown("### 🎯 Hedefe Göre Hesapla")
        hedef_harf = st.selectbox("Hedeflediğin Harf Notu Nedir?", ["AA", "BA", "BB", "CB", "CC", "DC", "DD", "FD"])
        
        # Harf notu barajları
        harf_barajlari = {"AA": 85, "BA": 80, "BB": 75, "CB": 70, "CC": 65, "DC": 60, "DD": 50, "FD": 40}
        gereken_toplam = harf_barajlari[hedef_harf]
        
        vize_katkisi = vize_notu * (vize_orani / 100)
        gereken_final = (gereken_toplam - vize_katkisi) / (final_orani / 100)
        gereken_final = round(gereken_final, 1)
        
        if gereken_final <= 0:
            st.balloons()
            st.success(f"Kanka rahat ol! Vize notun o kadar iyi ki, Finalde **0** bile alsan hedefin olan **{hedef_harf}** geliyor! 🎉")
        elif gereken_final > 100:
            st.error(f"Kanka vize biraz düşük kalmış... Finalden **{gereken_final}** alman lazım yani imkansızı zorlaman gerekiyor. Hedefi CC veya DC yapmayı dene bence.")
        else:
            st.warning(f"Hedeflediğin **{hedef_harf}** notunu yakalamak için Final sınavından en az **{gereken_final}** alman gerekiyor kanka. Sıkı çalış!")

    # SEKME 5: SOHBET ODASI
    with sekme5:
        st.subheader("💬 Bölüm Ortak Sohbet Odası")
        st.caption("Aynı linki kullanan herkes buraya yazabilir. Yapay zekayı çağırmak için mesajın başına @kahin yazın!")
        
        if not st.session_state["chat_isim"]:
            takma_ad = st.text_input("💬 Sohbet odası için bir Nickname (İsim) gir
