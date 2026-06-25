import streamlit as st
import google.generativeai as genai
from datetime import datetime
from pypdf import PdfReader
import io
import pandas as pd
import requests
import json
import time

# Sayfa Ayarları
st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

# --- CSS ---
st.markdown("""
<style>
    .stButton>button { width: 100% !important; border-radius: 12px !important; height: 45px !important; font-weight: bold !important; }
    .chat-box { padding: 12px; border-radius: 10px; margin-bottom: 8px; font-size: 14px; }
    .chat-user { background-color: #E3F2FD; border-left: 5px solid #1E88E5; }
    .chat-kahin { background-color: #FFF9C4; border-left: 5px solid #FBC02D; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# Session State
if "api_key_kayitli" not in st.session_state: st.session_state["api_key_kayitli"] = ""
if "chat_isim" not in st.session_state: st.session_state["chat_isim"] = ""
if "secilen_dersler" not in st.session_state: st.session_state["secilen_dersler"] = ["Finansal Muhasebe I"]
if "ders_notlari" not in st.session_state: st.session_state["ders_notlari"] = {}

# --- GİRİŞ KONTROLÜ ---
if not st.session_state["api_key_kayitli"]:
    st.title("🔮 Sınav Kahini Giriş")
    key = st.text_input("Gemini API Key:", type="password")
    if st.button("Giriş Yap"):
        st.session_state["api_key_kayitli"] = key
        st.rerun()
else:
    genai.configure(api_key=st.session_state["api_key_kayitli"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    st.title("🔮 Sınav Kahini")
    
    # TAB TANIMLAMA (Hatanın kaynağı burasıydı, burası tanımlı olmalı)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 Arşiv", "📢 Yükle", "📝 Soru", "📊 Hesapla", "💬 Sohbet"])

    # Diğer sekmeleri buraya senin kendi kodundaki gibi yerleştirebilirsin
    with tab1: st.write("Arşiv...")
    with tab2: st.write("Yükle...")
    with tab3: st.write("Soru...")
    with tab4: st.write("Hesapla...")

    # SOHBET SEKMESİ (Chat Kısmı)
    with tab5:
        st.subheader("💬 Bölüm Sohbeti")
        if not st.session_state["chat_isim"]:
            nick = st.text_input("Nickname:", key="nick_in")
            if st.button("Katıl", key="join_btn"):
                st.session_state["chat_isim"] = nick
                st.rerun()
        else:
            # Sohbeti buraya ekledik
            st.write(f"Hoş geldin, {st.session_state['chat_isim']}!")
            msg = st.text_input("Mesaj:", key="msg_in")
            if st.button("Gönder", key="send_btn"):
                st.success("Mesaj gönderildi!") # Buraya kendi Sheets kodunu ekleyebilirsin
                st.rerun()
            
            st.markdown("---")
            with st.expander("⚙️ Yönetici Paneli"):
                sifre = st.text_input("Şifre:", type="password")
                if sifre == "kahin123":
                    st.button("Tüm Sohbeti Sil")
