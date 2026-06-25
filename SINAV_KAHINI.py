import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import requests
import json
import time

st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

# --- MÜFREDAT HAVUZU ---
MÜFREDAT_HAVUZU = {
    "1. SINIF": ["İktisada Giriş I", "Genel Hukuk", "Genel İşletme", "Finansal Muhasebe I"],
    "2. SINIF": ["Finansal Okuryazarlık", "Şirketler Muhasebesi", "Stratejik Yönetim", "E-Ticaret"],
    "3. SINIF": ["Vergi Hukuku", "Finansal Yönetim I", "Maliyet Muhasebesi I", "Muhasebe Denetimi"],
    "4. SINIF": ["Muhasebe Standartları", "Yönetim Muhasebesi", "İnsan Kaynakları Yönetimi"]
}

# Session State
if "ders_notlari" not in st.session_state: st.session_state["ders_notlari"] = {}
if "secilen_dersler" not in st.session_state: st.session_state["secilen_dersler"] = ["Finansal Muhasebe I", "Ticaret Hukuku"]
if "api_key_kayitli" not in st.session_state: st.session_state["api_key_kayitli"] = ""
if "chat_isim" not in st.session_state: st.session_state["chat_isim"] = ""

# --- FONKSİYONLAR ---
def buluta_mesaj_yaz(tarih, isim, mesaj):
    try: requests.post("https://script.google.com/macros/s/AKfycbzExJPw5JDjfzInJ3_sPwNfv5en7aIVsl29vMHCtQlLIJq1fgZmxZrDDi6Y4SaYw6XuQA/exec", data=json.dumps({"tarih": tarih, "isim": isim, "mesaj": mesaj}))
    except: pass

# --- GİRİŞ ---
if not st.session_state["api_key_kayitli"]:
    st.title("🔮 Sınav Kahini Giriş")
    key = st.text_input("API Key:", type="password", key="login_key")
    if st.button("Giriş Yap", key="btn_log"):
        st.session_state["api_key_kayitli"] = key
        st.rerun()
else:
    genai.configure(api_key=st.session_state["api_key_kayitli"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    st.title("🔮 Sınav Kahini")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 Arşiv", "📢 Not Yükle", "📝 Soru", "📊 Hesapla", "💬 Chat"])

    with tab1:
        for ders in st.session_state["secilen_dersler"]:
            with st.expander(f"📁 {ders}"):
                if ders in st.session_state["ders_notlari"]:
                    for h, v in st.session_state["ders_notlari"][ders].items():
                        st.info(f"Hafta {h}: {v}")
                else: st.caption("Not yok.")

    with tab2:
        with st.popover("➕ Dönem Derslerini Düzenle"):
            gecici = []
            for sinif, liste in MÜFREDAT_HAVUZU.items():
                st.markdown(f"**{sinif}**")
                for d in liste:
                    if st.checkbox(d, value=(d in st.session_state["secilen_dersler"]), key=f"chk_{d}"):
                        gecici.append(d)
            if st.button("Kaydet", key="btn_save_ders"):
                st.session_state["secilen_dersler"] = gecici
                st.rerun()
        
        ders = st.selectbox("Ders:", st.session_state["secilen_dersler"], key="up_ders")
        hafta = st.number_input("Hafta:", 1, 14, 1, key="up_hafta")
        not_t = st.text_area("Not:", key="up_not")
        if st.button("Gönder", key="btn_up"):
            if ders not in st.session_state["ders_notlari"]: st.session_state["ders_notlari"][ders] = {}
            st.session_state["ders_notlari"][ders][hafta] = not_t
            st.success("Eklendi!")

    with tab4:
        st.warning("⚠️ ÖNEMLİ: Final barajı %50'dir. Çan eğrisi hesaplaması okulun belirlediği ortalamaya göre değişir.")
        vize = st.slider("Vize Notu", 0, 100, 50, key="v_s")
        v_oran = st.slider("Vize Yüzdesi", 10, 90, 40, key="v_o")
        sinif_ort = st.slider("Sınıf Ortalaması", 0, 100, 50, key="s_o")
        hedef = st.selectbox("Hedef Harf", ["AA", "BA", "BB", "CB", "CC"], key="h_s")
        
        baraj = {'AA':85,'BA':80,'BB':75,'CB':70,'CC':65}[hedef]
        gereken = round((baraj - (vize * (v_oran/100))) / ((100-v_oran)/100), 1)
        st.success(f"Hedefin olan {hedef} için Finalden alman gereken: **{gereken}**")

    with tab5:
        if not st.session_state["chat_isim"]:
            isim = st.text_input("İsim:", key="nick")
            if st.button("Katıl", key="btn_join"):
                st.session_state["chat_isim"] = isim
                st.rerun()
        else:
            try:
                df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/1qjPw6aNw1PFREblbFCd8ZZ5LnlxnmBLbDMLuV5dMb1I/gviz/tq?tqx=out:csv&cache_bust={time.time()}")
                for _, m in df.tail(15).iterrows():
                    st.markdown(f"**{m['isim']}**: {m['mesaj']}")
            except: pass
            
            yeni = st.text_input("Mesaj:", key="chat_msg")
            if st.button("Gönder", key="btn_chat"):
                buluta_mesaj_yaz(datetime.now().strftime("%H:%M"), st.session_state["chat_isim"], yeni)
                st.rerun()
