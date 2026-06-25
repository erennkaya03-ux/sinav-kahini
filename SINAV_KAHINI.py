import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import requests
import json
import time

# Sayfa Yapılandırması
st.set_page_config(page_title="Sınav Kahini - Orijinal", layout="centered")

# MÜFREDAT HAVUZU (Eski Düzenin Tamamı)
MÜFREDAT_HAVUZU = {
    "1. SINIF": ["İktisada Giriş I", "Genel Hukuk", "Bilgisayar Kullanımı", "Genel İşletme", "Finansal Muhasebe I", "İktisada Giriş II", "Yönetim ve Organizasyon", "Ticari Belgeler", "Ticari ve Mali Matematik", "Finansal Muhasebe II", "Ticaret Hukuku"],
    "2. SINIF": ["Finansal Okuryazarlık", "Finans Matematiği", "Muhasebe Paket Programları I", "Şirketler Muhasebesi", "Stratejik Yönetim", "Halkla İlişkiler", "İş ve Sosyal Güvenlik Hukuku", "Muhasebe Etiği", "E-Ticaret", "Para ve Sermaye Piyasası", "Finansal Tablolar Analizi", "İhtisas Muhasebesi", "Kıymetli Evrak Hukuku", "Girişimcilik", "İletişim Teknikleri", "Davranışsal İktisat", "Dış Ticaret İşlemleri", "Pazarlama Yönetimi"],
    "3. SINIF": ["Vergi Hukuku", "Yatırım Analizi", "Finansal Yönetim I", "Maliyet Muhasebesi I", "Sermaye Piyasası Mevzuatı", "Türkiye Ekonomisi", "Borsa İşlemleri", "Muhasebede Seçilmiş Konular", "İstatistik", "Enflasyon Muhasebesi", "Finansal Sistemler I", "Finansal Yönetim II", "Maliyet Muhasebesi II", "Türk Vergi Sistemi", "Muhasebe Denetimi", "Yatırım Kuruluşları", "Davranış Bilimleri", "Dış Ticaret Muhasebesi", "Sosyoloji"],
    "4. SINIF": ["Muhasebe Standartları", "Finansal Sistemler II", "Maliyet Yönetimi", "Davranışsal Finans", "Yönetim Muhasebesi", "Bilimsel Araştırma Yöntemleri", "Türev Piyasalar", "Muhasebe Bilgi Sistemleri", "Kobi Finansmanı", "İş Sağlığı ve Güvenliği", "İnsan Kaynakları", "Mesleki Eğitim"]
}

# Session Başlatma
if "secilen_dersler" not in st.session_state: st.session_state["secilen_dersler"] = ["Finansal Muhasebe I", "Ticaret Hukuku"]
if "ders_notlari" not in st.session_state: st.session_state["ders_notlari"] = {}
if "api_key" not in st.session_state: st.session_state["api_key"] = ""

# --- ARAYÜZ ---
st.title("🔮 Sınav Kahini - Orijinal Sistem")

if not st.session_state["api_key"]:
    st.session_state["api_key"] = st.text_input("🔑 API Key Gir:", type="password")
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 Arşiv", "📢 Not Yükle", "📝 Soru Odası", "📊 Hesapla", "💬 Sohbet"])

    # ARŞİV
    with tab1:
        st.subheader("📌 Ders Kütüphanen")
        for ders in st.session_state["secilen_dersler"]:
            with st.expander(f"📁 {ders}"):
                if ders in st.session_state["ders_notlari"]:
                    for h, n in st.session_state["ders_notlari"][ders].items():
                        st.info(f"Hafta {h}: {n}")
                else: st.caption("Bu derse not eklenmemiş.")

    # NOT YÜKLE
    with tab2:
        with st.popover("➕ Dersleri Düzenle"):
            yeni_liste = []
            for sinif, dersler in MÜFREDAT_HAVUZU.items():
                st.write(f"**{sinif}**")
                for d in dersler:
                    if st.checkbox(d, value=(d in st.session_state["secilen_dersler"]), key=f"ch_{d}"):
                        yeni_liste.append(d)
            if st.button("Kaydet", key="save_ders"):
                st.session_state["secilen_dersler"] = yeni_liste
                st.rerun()
        
        ders = st.selectbox("Ders Seç:", st.session_state["secilen_dersler"], key="up_d")
        hafta = st.number_input("Hafta:", 1, 14, 1, key="up_h")
        not_metin = st.text_area("Notunu Yaz:", key="up_t")
        if st.button("Kaydet", key="up_btn"):
            if ders not in st.session_state["ders_notlari"]: st.session_state["ders_notlari"][ders] = {}
            st.session_state["ders_notlari"][ders][hafta] = not_metin
            st.success("Not başarıyla kaydedildi!")

    # SORU ODASI
    with tab3:
        st.subheader("📝 Yapay Zeka Sınav Provası")
        ders = st.selectbox("Ders:", st.session_state["secilen_dersler"], key="q_d")
        if st.button("Soru Üret ve Çöz", key="q_btn"):
            genai.configure(api_key=st.session_state["api_key"])
            cevap = genai.GenerativeModel('gemini-2.5-flash').generate_content(f"{ders} dersinden 1 adet çıkması muhtemel vize/final sorusu ve cevabını ver.")
            st.write(cevap.text)

    # HESAPLA (Eski detaylı düzen)
    with tab4:
        st.warning("⚠️ Önemli Hatırlatma: Finalden en az 50 almadan geçemezsin. Çan eğrisi okul ortalamasına göre uygulanır.")
        vize = st.slider("Vize Notu", 0, 100, 50, key="h_v")
        v_oran = st.slider("Vize Etkisi (%)", 10, 90, 40, key="h_vo")
        sinif_ort = st.slider("Sınıf Ortalaması", 0, 100, 50, key="h_so")
        hedef = st.selectbox("Hedeflediğin Harf", ["AA", "BA", "BB", "CB", "CC", "DC"], key="h_target")
        
        # Hesaplama mantığı
        barajlar = {"AA": 90, "BA": 85, "BB": 80, "CB": 75, "CC": 70, "DC": 60}
        gereken = round((barajlar[hedef] - (vize * v_oran/100)) / ((100-v_oran)/100), 1)
        
        if gereken > 100: st.error("Kanka bu hedef şu vizeyle imkansız.")
        elif gereken < 0: st.success("Kanka rahatsın, 0 alsan da geçiyorsun!")
        else: st.info(f"Hedeflediğin {hedef} notu için finalden alman gereken: **{gereken}**")

    # SOHBET
    with tab5:
        st.write("Bölüm ortak sohbeti burada.")
