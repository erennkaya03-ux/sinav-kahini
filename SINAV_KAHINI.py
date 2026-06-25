import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import requests
import json
import time

# Sayfa Ayarları
st.set_page_config(page_title="Sınav Kahini", layout="wide")

# Müfredat Havuzu
MÜFREDAT_HAVUZU = {
    "1. SINIF": ["İktisada Giriş I", "Genel Hukuk", "Bilgisayar Kullanımı", "Genel İşletme", "Finansal Muhasebe I", "İktisada Giriş II", "Yönetim ve Organizasyon", "Ticari Belgeler", "Ticari ve Mali Matematik", "Finansal Muhasebe II", "Ticaret Hukuku"],
    "2. SINIF": ["Finansal Okuryazarlık", "Finans Matematiği", "Muhasebe Paket Programları I", "Şirketler Muhasebesi", "Stratejik Yönetim", "Halkla İlişkiler", "İş ve Sosyal Güvenlik Hukuku", "Muhasebe Etiği", "E-Ticaret", "Para ve Sermaye Piyasası", "Finansal Tablolar Analizi", "İhtisas Muhasebesi", "Kıymetli Evrak Hukuku", "Girişimcilik", "İletişim Teknikleri", "Davranışsal İktisat", "Dış Ticaret İşlemleri", "Pazarlama Yönetimi"],
    "3. SINIF": ["Vergi Hukuku", "Yatırım Analizi", "Finansal Yönetim I", "Maliyet Muhasebesi I", "Sermaye Piyasası Mevzuatı", "Türkiye Ekonomisi", "Borsa İşlemleri", "Muhasebede Seçilmiş Konular", "İstatistik", "Enflasyon Muhasebesi", "Finansal Sistemler I", "Finansal Yönetim II", "Maliyet Muhasebesi II", "Türk Vergi Sistemi", "Muhasebe Denetimi", "Yatırım Kuruluşları", "Davranış Bilimleri", "Dış Ticaret Muhasebesi", "Sosyoloji"],
    "4. SINIF": ["Muhasebe Standartları", "Finansal Sistemler II", "Maliyet Yönetimi", "Davranışsal Finans", "Yönetim Muhasebesi", "Bilimsel Araştırma Yöntemleri", "Türev Piyasalar", "Muhasebe Bilgi Sistemleri", "Kobi Finansmanı", "İş Sağlığı ve Güvenliği", "İnsan Kaynakları", "Mesleki Eğitim"]
}

# Session State Hazırlık
if "api_key" not in st.session_state: st.session_state["api_key"] = None
if "ders_notlari" not in st.session_state: st.session_state["ders_notlari"] = {}
if "secilen_dersler" not in st.session_state: st.session_state["secilen_dersler"] = ["Finansal Muhasebe I"]

# --- GİRİŞ KONTROLÜ (EN BAŞTA OLMALI) ---
if st.session_state["api_key"] is None:
    st.title("🔮 Sınav Kahini - Giriş")
    key = st.text_input("Gemini API Key:", type="password")
    if st.button("Giriş Yap"):
        st.session_state["api_key"] = key
        st.rerun()
    st.stop() # Giriş yapılmadıysa kodun devamını çalıştırma

# --- ANA UYGULAMA ---
st.title("🔮 Sınav Kahini")
genai.configure(api_key=st.session_state["api_key"])
model = genai.GenerativeModel('gemini-2.5-flash')

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 Arşiv", "📢 Not Yükle", "📝 Soru Odası", "📊 Hesapla", "💬 Sohbet"])

with tab1:
    st.subheader("📌 Ders Kütüphanen")
    for ders in st.session_state["secilen_dersler"]:
        with st.expander(f"📁 {ders}"):
            if ders in st.session_state["ders_notlari"]:
                for h, n in st.session_state["ders_notlari"][ders].items():
                    st.info(f"Hafta {h}: {n}")
            else: st.caption("Not henüz yok.")

with tab2:
    with st.popover("➕ Dersleri Düzenle"):
        yeni = []
        for sinif, liste in MÜFREDAT_HAVUZU.items():
            st.write(f"**{sinif}**")
            for d in liste:
                if st.checkbox(d, value=(d in st.session_state["secilen_dersler"]), key=f"ch_{d}"):
                    yeni.append(d)
        if st.button("Kaydet", key="sav"):
            st.session_state["secilen_dersler"] = yeni
            st.rerun()
    
    d_sec = st.selectbox("Ders Seç:", st.session_state["secilen_dersler"])
    hafta = st.number_input("Hafta:", 1, 14, 1)
    not_t = st.text_area("Notunu gir:")
    if st.button("Notu Kaydet"):
        if d_sec not in st.session_state["ders_notlari"]: st.session_state["ders_notlari"][d_sec] = {}
        st.session_state["ders_notlari"][d_sec][hafta] = not_t
        st.success("Not kaydedildi!")

with tab3:
    d_sec = st.selectbox("Soru İçin Ders:", st.session_state["secilen_dersler"], key="q_d")
    if st.button("Soru Üret"):
        cevap = model.generate_content(f"{d_sec} dersinden vize/final sınav sorusu üret ve çöz.").text
        st.write(cevap)

with tab4:
    st.warning("⚠️ Önemli: Finalden 50 altı alırsan FF ile kalırsın. Çan eğrisi okul ortalamasına göre uygulanır.")
    v = st.slider("Vize Notu", 0, 100, 50, key="v_s")
    v_oran = st.slider("Vize Etkisi (%)", 10, 90, 40, key="v_o")
    ort = st.slider("Sınıf Ortalaması", 0, 100, 50, key="c_s")
    h = st.selectbox("Hedef Harf", ["AA", "BA", "BB", "CB", "CC", "DC"], key="h_s")
    
    baraj = {"AA": 90, "BA": 85, "BB": 80, "CB": 75, "CC": 70, "DC": 60}[h]
    gereken = round((baraj - (v * v_oran/100)) / ((100-v_oran)/100), 1)
    st.success(f"{h} hedefi için finalden alman gereken: **{gereken}**")

with tab5:
    st.write("Bölüm sohbeti aktif.")
