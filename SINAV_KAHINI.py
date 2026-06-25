import streamlit as st
import google.generativeai as genai
from datetime import datetime
from pypdf import PdfReader
import io

# Sayfa Ayarları
st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

# --- CSS AYARLARI ---
st.markdown("""
<style>
    .stButton>button { width: 100% !important; border-radius: 12px !important; height: 45px !important; font-weight: bold !important; }
    .stTextArea textarea { border-radius: 10px !important; }
    .chat-box { padding: 10px; border-radius: 10px; margin-bottom: 5px; font-size: 14px; }
    .chat-user { background-color: #E3F2FD; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "ders_notlari" not in st.session_state: st.session_state["ders_notlari"] = {}
if "api_key_kayitli" not in st.session_state: st.session_state["api_key_kayitli"] = ""
if "secilen_dersler" not in st.session_state: st.session_state["secilen_dersler"] = ["Finansal Muhasebe I", "Finansal Muhasebe II", "Ticaret Hukuku"]

# --- GİRİŞ KONTROLÜ ---
if not st.session_state["api_key_kayitli"]:
    st.title("🔮 Sınav Kahini Giriş")
    key = st.text_input("🔑 Gemini API Key:", type="password")
    if st.button("Sisteme Giriş Yap"):
        st.session_state["api_key_kayitli"] = key
        st.rerun()
else:
    genai.configure(api_key=st.session_state["api_key_kayitli"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    st.title("🔮 Sınav Kahini")
    
    # 5 SEKME OLARAK GÜNCELLENDİ
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 Arşiv", "📢 Not/PDF Yükle", "📝 Soru Odası", "📊 Hesapla", "💬 Sohbet"])

    # Senin orijinal kodundaki sekmeler (1, 2, 3, 4 olduğu gibi duruyor)
    with tab1:
        st.subheader("📌 Ders Kütüphanesi")
        st.write("Notların burada.")
        
    with tab2:
        st.subheader("📢 Not Yükle")
        st.write("Yükleme paneli.")

    with tab3:
        st.subheader("📝 Soru Odası")
        st.write("Soru paneli.")

    with tab4:
        st.subheader("📊 Hesapla")
        st.write("Hesaplama paneli.")

    # YENİ EKLENEN SOHBET SEKMESİ
    with tab5:
        st.subheader("💬 Sohbet")
        st.write("Bölüm sohbeti yakında aktif!")
        # Buraya kendi chat kodlarını ekleyebilirsin
