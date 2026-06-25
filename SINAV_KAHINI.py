import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import requests
import json
import time
import random

# Sayfa Ayarları
st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

# CSS Stilleri
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 12px; height: 45px; font-weight: bold; }
    .chat-box { padding: 12px; border-radius: 10px; margin-bottom: 8px; font-size: 14px; }
    .chat-user { background-color: #E3F2FD; border-left: 5px solid #1E88E5; }
    .chat-kahin { background-color: #FFF9C4; border-left: 5px solid #FBC02D; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# Session State Hazırlığı
if "ders_notlari" not in st.session_state: st.session_state["ders_notlari"] = {}
if "api_key_kayitli" not in st.session_state: st.session_state["api_key_kayitli"] = ""
if "chat_isim" not in st.session_state: st.session_state["chat_isim"] = ""
if "secilen_dersler" not in st.session_state: st.session_state["secilen_dersler"] = ["Finansal Muhasebe I", "Finansal Muhasebe II", "Ticaret Hukuku"]

# Bağlantılar
SHEETS_YENI_LINK = "https://script.google.com/macros/s/AKfycbzExJPw5JDjfzInJ3_sPwNfv5en7aIVsl29vMHCtQlLIJq1fgZmxZrDDi6Y4SaYw6XuQA/exec"
SHEET_ID = "1qjPw6aNw1PFREblbFCd8ZZ5LnlxnmBLbDMLuV5dMb1I"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&cache_bust={int(time.time())}"

def buluta_mesaj_yaz(tarih, isim, mesaj):
    try: requests.post(SHEETS_YENI_LINK, data=json.dumps({"tarih": tarih, "isim": isim, "mesaj": mesaj}))
    except: pass

# Giriş Ekranı
if not st.session_state["api_key_kayitli"]:
    st.title("🔮 Sınav Kahini Giriş")
    key = st.text_input("🔑 API Key Girin:", type="password")
    if st.button("Sisteme Giriş Yap"):
        if key:
            st.session_state["api_key_kayitli"] = key.strip()
            st.rerun()
else:
    genai.configure(api_key=st.session_state["api_key_kayitli"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    st.title("🔮 Sınav Kahini")
    if st.button("🔒 Oturumu Kapat"):
        st.session_state["api_key_kayitli"] = ""
        st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 Arşiv", "📢 Not Yükle", "📝 Soru", "📊 Hesapla", "💬 Chat"])

    with tab1:
        st.subheader("📌 Ders Kütüphanesi")
        for ders in st.session_state["secilen_dersler"]:
            with st.expander(f"📁 {ders}", expanded=True):
                if ders in st.session_state["ders_notlari"]:
                    for h, v in st.session_state["ders_notlari"][ders].items():
                        st.markdown(f"**🗓️ {h}. Hafta**")
                        for i in v: st.info(i['icerik'])
                else: st.caption("Not yüklenmemiş.")

    with tab2:
        ders = st.selectbox("Ders:", st.session_state["secilen_dersler"])
        hafta = st.number_input("Hafta:", 1, 14, 1)
        not_metni = st.text_area("Notunuz:")
        if st.button("Gönder"):
            if ders not in st.session_state["ders_notlari"]: st.session_state["ders_notlari"][ders] = {}
            if hafta not in st.session_state["ders_notlari"][ders]: st.session_state["ders_notlari"][ders][hafta] = []
            st.session_state["ders_notlari"][ders][hafta].append({"tip": "metin", "icerik": not_metni})
            st.success("Eklendi!")

    with tab3:
        ders = st.selectbox("Ders:", st.session_state["secilen_dersler"], key="q_ders")
        if st.button("Soru Üret"):
            st.write(model.generate_content(f"{ders} dersinden bir sınav sorusu üret").text)

    with tab4:
        st.subheader("🎯 Hedef Hesapla")
        vize = st.slider("Vize?", 0, 100, 50)
        hedef = st.selectbox("Hedef:", ["AA", "BA", "BB", "CC"])
        st.info(f"Finalden en az {round((({'AA':85,'BA':80,'BB':75,'CC':65}[hedef] - (vize*0.4))/0.6), 1)} alman lazım.")

    with tab5:
        if not st.session_state["chat_isim"]:
            isim = st.text_input("Nickname:")
            if st.button("Katıl"):
                st.session_state["chat_isim"] = isim
                st.rerun()
        else:
            try:
                df = pd.read_csv(SHEET_CSV_URL)
                for _, m in df.tail(20).iterrows():
                    cls = "chat-kahin" if m['isim'] == "🔮 Kahin Bot" else "chat-user"
                    st.markdown(f"<div class='chat-box {cls}'><b>{m['isim']}:</b> {m['mesaj']}</div>", unsafe_allow_html=True)
            except: st.caption("Henüz mesaj yok.")
            
            yeni = st.text_input("Mesaj:")
            if st.button("Gönder"):
                buluta_mesaj_yaz(datetime.now().strftime("%H:%M"), st.session_state["chat_isim"], yeni)
                if "@kahin" in yeni:
                    buluta_mesaj_yaz("12:00", "🔮 Kahin Bot", model.generate_content(yeni).text)
                st.rerun()
            
            with st.expander("⚙️ Yönetici"):
                if st.text_input("Şifre", type="password") == "kahin123":
                    if st.button("Sıfırla"):
                        buluta_mesaj_yaz("CLEAR_CHAT", "SYSTEM", "ALL")
                        st.rerun()
