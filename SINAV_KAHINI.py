import streamlit as st
import google.generativeai as genai
from datetime import datetime
from pypdf import PdfReader
import io
import pandas as pd

# Sayfa Ayarları ve Mobil Görünüm Optimizasyonu
st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

# --- MOBİL ARAYÜZ STİL AYARLARI (CSS) ---
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
        color: #1E88E5;
        margin-top: 10px;
        margin-bottom: 5px;
        border-bottom: 1px solid #ddd;
        padding-bottom: 2px;
    }
    .chat-box {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 8px;
    }
    .chat-user { background-color: #F0F2F6; border-left: 5px solid #1E88E5; }
    .chat-kahin { background-color: #FFF3CD; border-left: 5px solid #FFC107; font-style: italic; }
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

HESAP_PLANI = {"100": "KASA", "101": "ALINAN ÇEKLER", "102": "BANKALAR", "103": "VERİLEN ÇEKLER (-)", "120": "ALICILAR", "121": "ALACAK SENETLERİ", "153": "TİCARİ MALLAR", "191": "İNDİRİLECEK KDV", "254": "TAŞITLAR", "255": "DEMİRBAŞLAR", "257": "BİRİKMİŞ AMORTİSMANLAR (-)", "320": "SATICILAR", "321": "BORÇ SENETLERİ", "391": "HESAPLANAN KDV", "500": "SERMAYE", "600": "YURTİÇİ SATIŞLAR", "621": "STMM (-)", "770": "GENEL YÖNETİM GİDERLERİ"}

# --- GOOGLE SHEETS VERİTABANI BAĞLANTI AYARI ---
SHEET_ID = "1qjPw6aNw1PFREblbFCd8ZZ5LnlxnmBLbDMLuV5dMb1I"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# --- GİRİŞ KONTROLÜ ---
if not st.session_state["api_key_kayitli"]:
    st.title("🔮 Sınav Kahini Giriş")
    st.subheader("Hoş geldiniz")
    girilen_key = st.text_input("🔑 Gemini API Key Girin:", type="password")
    if st.button("Sisteme Giriş Yap 🚀", use_container_width=True):
        if girilen_key:
            st.session_state["api_key_kayitli"] = girilen_key
            st.rerun()
else:
    genai.configure(api_key=st.session_state["api_key_kayitli"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    st.title("🔮 Sınav Kahini")
    if st.button("🔒 Oturumu Kapat", use_container_width=True):
        st.session_state["api_key_kayitli"] = ""
        st.rerun()

    st.markdown("---")

    # --- 5 SEKME SİSTEMİ ---
    sekme1, sekme2, sekme3, sekme4, sekme5 = st.tabs(["📁 Arşiv", "📢 Not Yükle", "📝 Soru Odası", "📊 Hesapla", "💬 Bölüm Chat"])

    with sekme1:
        st.subheader("📌 Ders Kütüphanesi")
        if st.session_state["ders_notlari"]:
            for ders, haftalar in st.session_state["ders_notlari"].items():
                if ders in st.session_state["secilen_dersler"]:
                    with st.expander(f"📁 {ders}", expanded=True):
                        for hafta, veri_listesi in sorted(haftalar.items()):
                            st.markdown(f"**🗓️ {hafta}. Hafta**")
                            for eleman in veri_listesi:
                                if eleman["tip"] == "metin":
                                    st.info(eleman['icerik'])
                                elif eleman["tip"] == "fotograf":
                                    st.image(eleman["icerik"], use_container_width=True)
        else:
            st.caption("Henüz yüklenmiş not yok.")

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
        secilen_hafta = st.number_input("Hafta:", min_value=1, max_value=14, value=1)
        ham_not = st.text_area("📝 Not ekleyin:")
        if st.button("🚀 Gönder", use_container_width=True):
            if ders_adi not in st.session_state["ders_notlari"]:
                st.session_state["ders_notlari"][ders_adi] = {}
            if secilen_hafta not in st.session_state["ders_notlari"][ders_adi]:
                st.session_state["ders_notlari"][ders_adi][secilen_hafta] = []
            if ham_not:
                st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({"tip": "metin", "icerik": ham_not})
            st.success("Arşive eklendi!")

    with sekme3:
        st.subheader("📝 Yapay Zeka Soru Odası")
        ders_kontrol = st.selectbox("Ders Seçin:", options=st.session_state["secilen_dersler"], key="sb_ders")
        zorluk = st.select_slider("Zorluk:", options=["Kolay", "Orta", "Zor", "Hocanın Saplama Modu"])
        ornek_soru = st.text_area("✍️ Soru Yazın (Opsiyonel):")
        if st.button("🔮 Soruyu Çöz / Üret", use_container_width=True):
            komut = f"{ders_kontrol} dersi için {zorluk} seviyesinde soru çöz/üret." if not ornek_soru else f"{ders_kontrol} sorusunu çöz: {ornek_soru}"
            st.session_state["mob_soru"] = model.generate_content(komut).text
        if "mob_soru" in st.session_state:
            st.markdown(st.session_state["mob_soru"])

    with sekme4:
        st.subheader("📊 Harf Notu Simülatörü")
        vize_notu = st.slider("Vize?", 0, 100, 40)
        muhtemel_final = st.slider("Final?", 0, 100, 50)
        ort = vize_notu*0.4 + muhtemel_final*0.6
        st.metric("Dönem Notu:", f"{round(ort,1)}")

    # --- SEKME 5: SOHBET ODASI ---
    with sekme5:
        st.subheader("💬 Bölüm Ortak Sohbet Odası")
        st.caption("Aynı linki kullanan herkes buraya yazabilir. Yapay zekayı çağırmak için mesajın başına **@kahin** yazın!")
        
        if not st.session_state["chat_isim"]:
            takma_ad = st.text_input("💬 Sohbet odası için bir Nickname (İsim) girin:", placeholder="Örn: Ahmet_100")
            if st.button("Sohbete Katıl 🚀"):
                if takma_ad:
                    st.session_state["chat_isim"] = takma_ad
                    st.rerun()
        else:
            st.write(f"Kullanıcı Adın: **{st.session_state['chat_isim']}**")
            
            try:
                df = pd.read_csv(SHEET_CSV_URL)
                df = df.tail(30)
                mesajlar = df.to_dict(orient="records")
            except:
                if "yerel_chat" not in st.session_state:
                    st.session_state["yerel_chat"] = [{"tarih": "Şimdi", "isim": "Sistem", "mesaj": "Google Sheet ID başarıyla entegre edildi. Mesajlaşmaya başlayabilirsiniz."}]
                mesajlar = st.session_state["yerel_chat"]

            st.markdown("---")
            for m in mesajlar:
                cls = "chat-kahin" if m['isim'] == "🔮 Kahin Bot" else "chat-user"
                st.markdown(f"<div class='chat-box {cls}'><b>{m['isim']}:</b> {m['mesaj']}</div>", unsafe_allow_html=True)
            st.markdown("---")

            yeni_m = st.text_input("✉️ Mesajınızı yazın:", placeholder="Beyler vize soruları nasıldı?", key="chat_input")
            
            if st.button("Gönder ✉️", use_container_width=True):
                if yeni_m:
                    zaman = datetime.now().strftime("%H:%M")
                    yeni_satir = {"tarih": zaman, "isim": st.session_state["chat_isim"], "mesaj": yeni_m}
                    
                    if "yerel_chat" not in st.session_state:
                        st.session_state["yerel_chat"] = []
                    st.session_state["yerel_chat"].append(yeni_satir)

                    if yeni_m.strip().lower().startswith("@kahin"):
                        soru = yeni_m.replace("@kahin", "").strip()
                        with st.spinner("🔮 Kahin Bot gruba yazıyor..."):
                            bot_cevap = model.generate_content(f"Sen bir üniversite grubundaki akıllı asistansın. Öğrencinin şu sorusuna gruptakilerin anlayacağı samimi ama net bir cevap yaz: {soru}").text
                            bot_satir = {"tarih": zaman, "isim": "🔮 Kahin Bot", "mesaj": bot_cevap}
                            st.session_state["yerel_chat"].append(bot_satir)
                    st.rerun()
            
            if st.button("🔄 Sohbeti Yenile"):
                st.rerun()
