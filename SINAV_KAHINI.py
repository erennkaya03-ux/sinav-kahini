import streamlit as st
import google.generativeai as genai

# Sayfa ayarları
st.set_page_config(page_title="Sınav Kahini", layout="centered")

# Session state kontrolleri
if "api_key" not in st.session_state: st.session_state["api_key"] = None
if "giris_yapildi" not in st.session_state: st.session_state["giris_yapildi"] = False

# GİRİŞ EKRANI
if not st.session_state["giris_yapildi"]:
    st.title("🔮 Sınav Kahini - Giriş")
    key = st.text_input("Gemini API Key:", type="password")
    if st.button("Sisteme Giriş Yap"):
        if key:
            st.session_state["api_key"] = key
            st.session_state["giris_yapildi"] = True
            st.rerun()
else:
    # ANA SİSTEM
    st.title("🔮 Sınav Kahini")
    if st.button("Çıkış Yap"):
        st.session_state["giris_yapildi"] = False
        st.rerun()
        
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Arşiv", "📝 Soru", "📊 Hesapla", "💬 Chat"])

    with tab1:
        st.subheader("📌 Arşiv")
        st.write("Ders notların burada listelenecek.")
        
    with tab2:
        st.subheader("📝 Soru Odası")
        d = st.selectbox("Ders:", ["Finansal Muhasebe I", "Ticaret Hukuku", "Genel Hukuk"])
        if st.button("Soru Üret"):
            st.write(f"{d} için örnek soru...")

    with tab3:
        st.subheader("📊 Harf Notu Hesapla")
        st.warning("⚠️ Önemli: Çan eğrisi okul ortalamasına göre değişir.")
        v = st.slider("Vize Notu", 0, 100, 50)
        v_o = st.slider("Vize Etkisi (%)", 10, 90, 40)
        hedef = st.selectbox("Hedef:", ["AA", "BA", "BB", "CB", "CC"])
        baraj = {'AA':90,'BA':85,'BB':80,'CB':75,'CC':70}[hedef]
        st.success(f"{hedef} için finalden: {round((baraj - (v * v_o/100)) / ((100-v_o)/100), 1)} alman lazım.")

    with tab4:
        st.write("Sohbet odası.")
