import streamlit as st
import google.generativeai as genai
from datetime import datetime
import time

# Sayfa Ayarları
st.set_page_config(page_title="Sınav Kahini", layout="centered")

# MÜFREDAT HAVUZU
MÜFREDAT_HAVUZU = {
    "1. SINIF": ["İktisada Giriş I", "Genel Hukuk", "Bilgisayar Kullanımı", "Genel İşletme", "Finansal Muhasebe I", "İktisada Giriş II", "Yönetim ve Organizasyon", "Ticari Belgeler", "Ticari ve Mali Matematik", "Finansal Muhasebe II", "Ticaret Hukuku"],
    "2. SINIF": ["Finansal Okuryazarlık", "Finans Matematiği", "Muhasebe Paket Programları I", "Şirketler Muhasebesi", "Stratejik Yönetim", "Halkla İlişkiler", "İş ve Sosyal Güvenlik Hukuku", "Muhasebe Etiği", "E-Ticaret", "Para ve Sermaye Piyasası", "Finansal Tablolar Analizi", "İhtisas Muhasebesi", "Kıymetli Evrak Hukuku", "Girişimcilik", "İletişim Teknikleri", "Davranışsal İktisat", "Dış Ticaret İşlemleri", "Pazarlama Yönetimi"],
    "3. SINIF": ["Vergi Hukuku", "Yatırım Analizi", "Finansal Yönetim I", "Maliyet Muhasebesi I", "Sermaye Piyasası Mevzuatı", "Türkiye Ekonomisi", "Borsa İşlemleri", "Muhasebede Seçilmiş Konular", "İstatistik", "Enflasyon Muhasebesi", "Finansal Sistemler I", "Finansal Yönetim II", "Maliyet Muhasebesi II", "Türk Vergi Sistemi", "Muhasebe Denetimi", "Yatırım Kuruluşları", "Davranış Bilimleri", "Dış Ticaret Muhasebesi", "Sosyoloji"],
    "4. SINIF": ["Muhasebe Standartları", "Finansal Sistemler II", "Maliyet Yönetimi", "Davranışsal Finans", "Yönetim Muhasebesi", "Bilimsel Araştırma Yöntemleri", "Türev Piyasalar", "Muhasebe Bilgi Sistemleri", "Kobi Finansmanı", "İş Sağlığı ve Güvenliği", "İnsan Kaynakları", "Mesleki Eğitim"]
}

# Session State
if "secilen_dersler" not in st.session_state: st.session_state["secilen_dersler"] = ["Finansal Muhasebe I", "Ticaret Hukuku"]
if "ders_notlari" not in st.session_state: st.session_state["ders_notlari"] = {}
if "api_key" not in st.session_state: st.session_state["api_key"] = None

# Giriş
if st.session_state["api_key"] is None:
    st.title("🔮 Sınav Kahini")
    key = st.text_input("API Key Gir:", type="password")
    if st.button("Giriş Yap"):
        st.session_state["api_key"] = key
        st.rerun()
else:
    st.title("🔮 Sınav Kahini")
    if st.button("Çıkış"):
        st.session_state["api_key"] = None
        st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["📁 Arşiv", "📢 Not Yükle", "📝 Soru Odası", "📊 Hesapla"])

    # ARŞİV
    with tab1:
        for ders in st.session_state["secilen_dersler"]:
            with st.expander(f"📁 {ders}"):
                if ders in st.session_state["ders_notlari"]:
                    for h, n in st.session_state["ders_notlari"][ders].items():
                        st.info(f"Hafta {h}: {n}")
                else: st.caption("Not yok.")

    # NOT YÜKLE
    with tab2:
        with st.popover("➕ Ders Düzenle"):
            yeni = []
            for sinif, liste in MÜFREDAT_HAVUZU.items():
                st.write(f"**{sinif}**")
                for d in liste:
                    if st.checkbox(d, value=(d in st.session_state["secilen_dersler"]), key=f"ch_{d}"):
                        yeni.append(d)
            if st.button("Kaydet", key="sav_d"):
                st.session_state["secilen_dersler"] = yeni
                st.rerun()
        
        d = st.selectbox("Ders:", st.session_state["secilen_dersler"])
        h = st.number_input("Hafta:", 1, 14, 1)
        n = st.text_area("Not:")
        if st.button("Kaydet", key="sav_n"):
            if d not in st.session_state["ders_notlari"]: st.session_state["ders_notlari"][d] = {}
            st.session_state["ders_notlari"][d][h] = n
            st.success("Eklendi!")

    # SORU ODASI
    with tab3:
        d = st.selectbox("Ders:", st.session_state["secilen_dersler"], key="q_d")
        if st.button("Soru Üret"):
            genai.configure(api_key=st.session_state["api_key"])
            st.write(genai.GenerativeModel('gemini-2.5-flash').generate_content(f"{d} için soru üret.").text)

    # HESAPLA
    with tab4:
        st.warning("⚠️ Final barajı 50'dir.")
        v = st.slider("Vize", 0, 100, 50)
        v_o = st.slider("Vize Yüzdesi", 10, 90, 40)
        h = st.selectbox("Hedef:", ["AA", "BA", "BB", "CB", "CC"])
        baraj = {'AA':90,'BA':85,'BB':80,'CB':75,'CC':70}[h]
        st.success(f"{h} için finalden: {round((baraj - (v * v_o/100)) / ((100-v_o)/100), 1)} alman lazım.")
