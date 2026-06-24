import streamlit as st
import google.generativeai as genai
from datetime import datetime
from pypdf import PdfReader
import io

# Sayfa Ayarları ve Mobil Görünüm Optimizasyonu
st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

# --- MOBİL ARAYÜZ STİL AYARLARI (CSS) ---
st.markdown("""
<style>
    /* Telefonlarda input alanlarını ve butonları daha belirgin yap */
    .stButton>button {
        width: 100% !important;
        border-radius: 12px !important;
        height: 45px !important;
        font-weight: bold !important;
    }
    .stTextArea textarea {
        border-radius: 10px !important;
    }
    /* Mobil sekmeleri daha geniş ve dokunmatik yap */
    button[data-baseweb="tab"] {
        font-size: 14px !important;
        padding: 10px 5px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SANAL HAFIZA KURULUMU ---
if "ders_notlari" not in st.session_state:
    st.session_state["ders_notlari"] = {}

if "baslangic_tarihi" not in st.session_state:
    st.session_state["baslangic_tarihi"] = datetime.now()

if "gecici_pdf_ozeti" not in st.session_state:
    st.session_state["gecici_pdf_ozeti"] = None

# --- TEK DÜZEN HESAP PLANI VERİTABANI ---
HESAP_PLANI = {"100": "KASA", "101": "ALINAN ÇEKLER", "102": "BANKALAR", "103": "VERİLEN ÇEKLER (-)", "120": "ALICILAR", "121": "ALACAK SENETLERİ", "153": "TİCARİ MALLAR", "191": "İNDİRİLECEK KDV", "254": "TAŞITLAR", "255": "DEMİRBAŞLAR", "257": "BİRİKMİŞ AMORTİSMANLAR (-)", "320": "SATICILAR", "321": "BORÇ SENETLERİ", "391": "HESAPLANAN KDV", "500": "SERMAYE", "600": "YURTİÇİ SATIŞLAR", "621": "STMM (-)", "770": "GENEL YÖNETİM GİDERLERİ"}

st.title("🔮 Sınav Kahini Mobil")

# Mobil Güvenlik Girişi (Ana Ekranda En Üstte)
user_api_key = st.text_input("🔑 Gemini API Key Girin:", type="password", help="Google AI Studio'dan aldığın ücretsiz anahtarı buraya yapıştır kanka.")

if user_api_key:
    genai.configure(api_key=user_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.warning("⚠️ Sistemi çalıştırmak için lütfen yukarıya API anahtarını yapıştır kanka.")

# KORUMA KALKANI: Şifre yoksa alt sekmeleri yükleme
if not user_api_key:
    st.info("💡 **Nasıl Ücretsiz Şifre Alırım?**\n1. [Google AI Studio](https://aistudio.google.com/) sitesine git.\n2. Giriş yapıp **'Get API Key'** butonuna bas.\n3. Kodu kopyala ve yukarıdaki kutuya yapıştır!")
else:
    # --- MOBİL ÜST SEKME SİSTEMİ ---
    sekme1, sekme2, sekme3, sekme4 = st.tabs(["📁 Arşiv", "📢 Not Yükle", "📝 Soru Odası", "📊 Hesapla"])

    # SEKME 1: DERS ARŞİVİ
    with sekme1:
        st.subheader("📌 Ders Kütüphanen")
        if st.session_state["ders_notlari"]:
            for ders, haftalar in st.session_state["ders_notlari"].items():
                with st.expander(f"📁 {ders}", expanded=True):
                    for hafta, veri_listesi in sorted(haftalar.items()):
                        st.markdown(f"**🗓️ {hafta}. Hafta**")
                        for idx, eleman in enumerate(veri_listesi):
                            if eleman["tip"] == "metin":
                                st.info(eleman['icerik'])
                            elif eleman["tip"] == "fotograf":
                                st.image(eleman["icerik"], use_container_width=True)
                        if st.button(f"🗑️ {hafta}. Haftayı Temizle", key=f"del_{ders}_{hafta}", use_container_width=True):
                            del st.session_state["ders_notlari"][ders][hafta]
                            st.rerun()
        else:
            st.caption("Henüz yüklenmiş bir ders notu yok kanka.")

    # SEKME 2: HOCANIN AĞZINDAN (NOT YÜKLEME)
    with sekme2:
        st.subheader("📢 Hocanın Ağzından")
        ders_adi = st.selectbox("Ders:", ["Finansal Muhasebe", "Ticaret Hukuku", "Makro İktisat"], key="mob_ders")
        secilen_hafta = st.number_input("Hafta:", min_value=1, max_value=14, value=1, key="mob_hafta")
        
        st.markdown("---")
        ham_not = st.text_area("📝 Hocanın lafını karala veya yapıştır:", placeholder="Hoca buraya yıldız koydu...", height=100)
        yuklenen_foto = st.file_uploader("📸 Tahta Fotoğrafı Yükle:", type=["png", "jpg", "jpeg"])
        
        if st.button("🚀 Havuza Gönder", use_container_width=True):
            if ham_not or yuklenen_foto:
                if ders_adi not in st.session_state["ders_notlari"]:
                    st.session_state["ders_notlari"][ders_adi] = {}
                if secilen_hafta not in st.session_state["ders_notlari"][ders_adi]:
                    st.session_state["ders_notlari"][ders_adi][secilen_hafta] = []
                
                if ham_not:
                    st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({"tip": "metin", "icerik": ham_not})
                if yuklenen_foto:
                    st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({"tip": "fotograf", "icerik": yuklenen_foto.read()})
                st.success("Havuza fırlatıldı! 📁")
                st.rerun()

    # SEKME 3: SINAV KAHİNİ (SORU ODASI)
    with sekme3:
        st.subheader("📝 Yapay Zeka Soru Odası")
        ders_kontrol = st.selectbox("Ders Seçin:", ["Finansal Muhasebe", "Ticaret Hukuku", "Makro İktisat"], key="kahin_mob_ders")
        zorluk = st.select_slider("Zorluk:", options=["Kolay", "Orta", "Zor", "Hocanın Saplama Modu"], key="mob_zorluk")
        
        if st.button("🔮 Yapay Zekaya Soru Ürettir", use_container_width=True):
            komut = f"Sen üniversitede {ders_kontrol} dersi veren bir hocasın. {zorluk} seviyesinde bir sınav sorusu ve hemen altına detaylı adım adım çözümünü üret kanka. Arada mutlaka '---' kullan."
            with st.spinner("🔮 Soru hazırlanıyor..."):
                try:
                    response = model.generate_content(komut)
                    st.session_state["mob_soru"] = response.text
                except Exception as e:
                    st.error(f"Hata: {e}")
                    
        if "mob_soru" in st.session_state:
            st.markdown(st.session_state["mob_soru"])

    # SEKME 4: HARF NOTU HESAPLAMA
    with sekme4:
        st.subheader("📊 Harf Notu Garantör")
        vize_notu = st.slider("Vize Notun?", min_value=0, max_value=100, value=40, key="mob_vize")
        sinif_ort = st.slider("Sınıf Ortalaması?", min_value=20, max_value=80, value=45, key="mob_ort")
        
        st.markdown("---")
        # Basit hedef hesabı (CC için gereken final)
        vize_katki = vize_notu * 0.4
        gereken_final = (sinif_ort - vize_katki) / 0.6
        gereken_final = max(45.0, gereken_final)
        
        if gereken_final > 100:
            st.error("🚨 Sınıf ortalamasına göre geçmen imkansız görünüyor kanka!")
        else:
            st.metric(label="🎯 CC ile Geçmek İçin Gereken Final:", value=f"{round(gereken_final, 1)}")
