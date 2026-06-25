import streamlit as st
import google.generativeai as genai
from datetime import datetime
from pypdf import PdfReader
import io

st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

st.markdown("""
<style>
    .stButton>button { width: 100% !important; border-radius: 12px !important; height: 45px !important; font-weight: bold !important; }
    .stTextArea textarea { border-radius: 10px !important; }
    button[data-baseweb="tab"] { font-size: 14px !important; padding: 10px 5px !important; }
    .ders-baslik { font-weight: bold; color: #1E88E5; margin-top: 10px; margin-bottom: 5px; border-bottom: 1px solid #ddd; padding-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

if "ders_notlari" not in st.session_state: st.session_state["ders_notlari"] = {}
if "api_key_kayitli" not in st.session_state: st.session_state["api_key_kayitli"] = ""

MÜFREDAT_HAVUZU = {
    "1. SINIF DERSLERİ": ["İktisada Giriş I", "Genel Hukuk", "Bilgisayar Kullanımı ve Ofis Uygulamaları", "Genel İşletme", "Finansal Muhasebe I", "İktisada Giriş II", "Yönetim ve Organizasyon", "Ticari Belgeler", "Ticari ve Mali Matematik", "Finansal Muhasebe II", "Ticaret Hukuku"],
    "2. SINIF DERSLERİ": ["Finansal Okuryazarlık", "Finans Matematiği", "Muhasebe Paket Programları I", "Şirketler Muhasebesi", "Stratejik Yönetim", "Halkla İlişkiler", "İş ve Sosyal Güvenlik Hukuku", "Muhasebe Meslek Mevzuatı ve Etiği", "E-Ticaret", "Muhasebe Paket Programları II", "Para ve Sermaye Piyasası Kurumları", "Finansal Tablolar Analizi", "İhtisas Muhasebesi", "Kıymetli Evrak Hukuku", "Girişimcilik", "İletişim ve Etkili Sunum Teknikleri", "Davranışsal İktisat", "Dış Ticaret İşlemleri", "Pazarlama Yönetimi"],
    "3. SINIF DERSLERİ": ["Vergi Hukuku", "Yatırım Analizi ve Portföy Yönetimi", "Finansal Yönetim I", "Maliyet Muhasebesi I", "Sermaye Piyasası Mevzuatı", "Türkiye Ekonomisi", "Borsa İşlemleri", "Muhasebede Seçilmiş Konular ve Örnek Olaylar", "İstatistik", "Enflasyon Muhasebesi", "Finansal Sistem ve Uygulamaları I", "Finansal Yönetim II", "Maliyet Muhasebesi II", "Türk Vergi Sistemi ve Uygulamaları", "Muhasebe Denetimi", "Yatırım Kuruluşları ve Araçları", "Yönlendirilmiş Çalışmalar", "Davranış Bilimleri", "Dış Ticaret İşlemleri Muhasebesi", "Sosyoloji"],
    "4. SINIF DERSLERİ": ["Muhasebe Standartları", "Finansal Sistem ve Uygulamaları II", "Maliyet Yönetimi", "Davranışsal Finans", "Yönetim Muhasebesi", "Bilimsel Araştırma Yöntemleri", "Türev Piyasalar ve Risk Yönetimi", "Muhasebe Bilgi Sistemleri", "Kobi Finansmanı", "İş Sağlığı ve Güvenliği", "İnsan Kaynakları Yönetimi", "İşletmede Mesleki Eğitim"]
}

if "secilen_dersler" not in st.session_state: st.session_state["secilen_dersler"] = ["Finansal Muhasebe I", "Finansal Muhasebe II", "Ticaret Hukuku"]

if not st.session_state["api_key_kayitli"]:
    st.title("🔮 Sınav Kahini Giriş")
    girilen_key = st.text_input("🔑 Gemini API Key Girin:", type="password")
    if st.button("Sisteme Giriş Yap 🚀", use_container_width=True):
        if girilen_key:
            st.session_state["api_key_kayitli"] = girilen_key
            st.rerun()
else:
    genai.configure(api_key=st.session_state["api_key_kayitli"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    st.title("🔮 Sınav Kahini")
    
    if st.button("🔒 Oturumu Kapat / Key Değiştir", use_container_width=True):
        st.session_state["api_key_kayitli"] = ""
        st.rerun()

    st.markdown("---")

    # BURASI ÖNEMLİ: 5 SEKMEYİ TANIMLIYORUZ
    sekme1, sekme2, sekme3, sekme4, sekme5 = st.tabs(["📁 Arşiv", "📢 Not/PDF Yükle", "📝 Soru Odası", "📊 Hesapla", "💬 Sohbet"])

    # SEKME 1 (Orijinal Kod)
    with sekme1:
        st.subheader("📌 Ders Kütüphanesi")
        if st.session_state["ders_notlari"]:
            aktif_arsiv_var_mi = False
            for ders, haftalar in st.session_state["ders_notlari"].items():
                if ders in st.session_state["secilen_dersler"]:
                    aktif_arsiv_var_mi = True
                    with st.expander(f"📁 {ders}", expanded=True):
                        for hafta, veri_listesi in sorted(haftalar.items()):
                            st.markdown(f"**🗓️ {hafta}. Hafta**")
                            for eleman in veri_listesi:
                                if eleman["tip"] == "metin": st.info(eleman['icerik'])
                                elif eleman["tip"] == "fotograf": st.image(eleman["icerik"], use_container_width=True)
                            if st.button(f"🗑️ {hafta}. Haftayı Temizle", key=f"del_{ders}_{hafta}"):
                                del st.session_state["ders_notlari"][ders][hafta]
                                st.rerun()
        else: st.caption("Henüz not yok.")

    # SEKME 2 (Orijinal Kod)
    with sekme2:
        st.subheader("📢 Not ve PDF Yükle")
        with st.popover("➕ Ders Düzenle"):
            gecici_secimler = []
            for sinif, liste in MÜFREDAT_HAVUZU.items():
                st.markdown(f"**{sinif}**")
                for d in liste:
                    if st.checkbox(d, value=(d in st.session_state["secilen_dersler"])): gecici_secimler.append(d)
            if st.button("Listeyi Güncelle"):
                st.session_state["secilen_dersler"] = gecici_secimler
                st.rerun()
        
        ders_adi = st.selectbox("Ders:", options=st.session_state["secilen_dersler"])
        secilen_hafta = st.number_input("Hafta:", 1, 14, 1)
        ham_not = st.text_area("Not:")
        if st.button("🚀 Kaydet"):
            if ders_adi not in st.session_state["ders_notlari"]: st.session_state["ders_notlari"][ders_adi] = {}
            if secilen_hafta not in st.session_state["ders_notlari"][ders_adi]: st.session_state["ders_notlari"][ders_adi][secilen_hafta] = []
            st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({"tip": "metin", "icerik": ham_not})
            st.rerun()

    # SEKME 3 (Orijinal Kod)
    with sekme3:
        st.subheader("📝 Yapay Zeka Soru Odası")
        ders_k = st.selectbox("Ders:", options=st.session_state["secilen_dersler"])
        if st.button("🔮 Soru Üret"):
            st.write(model.generate_content(f"{ders_k} için bir soru üret ve çöz.").text)

    # SEKME 4 (Orijinal Kod)
    with sekme4:
        st.subheader("📊 Harf Notu & Geçme")
        vize = st.slider("Vize", 0, 100, 40)
        final = st.slider("Final", 0, 100, 50)
        st.success(f"Ortalama: {(vize*0.4) + (final*0.6)}")

    # SEKME 5 (CHAT EKLENTİSİ)
    with sekme5:
        st.subheader("💬 Sohbet")
        st.text_input("Mesajınız:", key="chat_in")
        if st.button("Gönder"): st.success("Mesaj gönderildi!")
        with st.expander("⚙️ Yönetici Paneli"):
            if st.text_input("Şifre:", type="password") == "admin123":
                st.button("🚫 Kullanıcıyı Sustur")
                st.button("🗑️ Sohbeti Sil")
